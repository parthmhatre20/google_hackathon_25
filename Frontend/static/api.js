// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// State management
const appState = {
    currentQuestions: [],
    currentQuestionIndex: 0,
    userId: null,
    domain: null,
    resumeText: null,
    mediaRecorder: null,
    audioChunks: [],
    isRecording: false
};

// ==================== Resume & Question Generation ====================

async function handleMockInterviewSubmit(event) {
    event.preventDefault();
    
    const jobRole = document.getElementById('job-role').value;
    const cvFile = document.getElementById('cv-upload').files[0];
    
    if (!jobRole) {
        showNotification('Please select a job role', 'error');
        return;
    }
    
    // Extract resume text
    let resumeText = '';
    if (cvFile) {
        resumeText = await extractTextFromFile(cvFile);
    } else {
        // If no CV, use job role as context
        resumeText = `Applying for ${jobRole} position. General software engineering background.`;
    }
    
    appState.domain = jobRole;
    appState.resumeText = resumeText;
    
    // Show loading state
    showNotification('Generating personalized questions...', 'info');
    
    try {
        // Call your backend API
        const response = await fetch(`${API_BASE_URL}/interview/generate-questions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resume_text: resumeText,
                domain: jobRole,
                num_questions: 5
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate questions');
        }
        
        const data = await response.json();
        appState.currentQuestions = data.questions;
        appState.currentQuestionIndex = 0;
        
        // Switch to chat view and display first question
        displayQuestion(0);
        document.getElementById('main-view').dataset.view = 'chat';
        
        showNotification('Questions generated! Let\'s begin.', 'success');
        
    } catch (error) {
        console.error('Error generating questions:', error);
        showNotification('Failed to generate questions. Using fallback.', 'error');
        
        // Fallback to default questions
        appState.currentQuestions = getDefaultQuestions();
        displayQuestion(0);
        document.getElementById('main-view').dataset.view = 'chat';
    }
}

async function extractTextFromFile(file) {
    // For now, just return filename as placeholder
    // In production, you'd parse PDF/DOC files
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            // Basic text extraction (works for .txt files)
            resolve(e.target.result || `Experience with ${file.name.split('.')[0]}`);
        };
        reader.onerror = () => {
            resolve('Software engineering experience.');
        };
        
        if (file.type === 'text/plain') {
            reader.readAsText(file);
        } else {
            // For PDF/DOC, you'd need a library. For now, use filename
            resolve(`Professional experience in software development. CV: ${file.name}`);
        }
    });
}

function getDefaultQuestions() {
    return [
        { question_id: 'q1', question_text: 'Tell me about yourself.', category: 'general' },
        { question_id: 'q2', question_text: 'What are your greatest strengths?', category: 'behavioral' },
        { question_id: 'q3', question_text: 'Describe a challenging project you worked on.', category: 'technical' }
    ];
}

// ==================== Question Display ====================

function displayQuestion(index) {
    if (index >= appState.currentQuestions.length) {
        showInterviewComplete();
        return;
    }
    
    const question = appState.currentQuestions[index];
    const chatMessages = document.getElementById('chat-messages');
    
    if (!chatMessages) return;
    
    // Clear previous messages or append
    const questionHTML = `
        <div class="flex gap-4 mb-6">
            <div class="w-10 h-10 rounded-full bg-indigo-500/10 flex items-center justify-center shrink-0">
                <i data-lucide="bot" class="w-5 h-5 text-indigo-400"></i>
            </div>
            <div class="flex-1">
                <div class="text-sm text-zinc-500 mb-2">AI Interviewer</div>
                <div class="bg-zinc-900 border border-zinc-800 rounded-2xl p-4">
                    <p class="text-zinc-200 leading-relaxed">${question.question_text}</p>
                    ${question.reasoning ? `<p class="text-xs text-zinc-500 mt-2">Focus: ${question.reasoning}</p>` : ''}
                </div>
            </div>
        </div>
    `;
    
    chatMessages.innerHTML += questionHTML;
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Re-initialize lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// ==================== Audio Recording ====================

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        appState.mediaRecorder = new MediaRecorder(stream);
        appState.audioChunks = [];
        
        appState.mediaRecorder.ondataavailable = (event) => {
            appState.audioChunks.push(event.data);
        };
        
        appState.mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(appState.audioChunks, { type: 'audio/wav' });
            await processAudio(audioBlob);
        };
        
        appState.mediaRecorder.start();
        appState.isRecording = true;
        
        // Update UI
        document.getElementById('recording-bar').dataset.state = 'listening';
        document.getElementById('AI-listening').dataset.state = 'listening';
        document.getElementById('timer').dataset.state = 'listening';
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        showNotification('Could not access microphone', 'error');
    }
}

function stopRecording() {
    if (appState.mediaRecorder && appState.isRecording) {
        appState.mediaRecorder.stop();
        appState.isRecording = false;
        
        // Update UI
        document.getElementById('recording-bar').dataset.state = 'idle';
        document.getElementById('AI-listening').dataset.state = 'idle';
        document.getElementById('timer').dataset.state = 'idle';
        
        // Stop all tracks
        appState.mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
}

// ==================== Audio Processing ====================

async function processAudio(audioBlob) {
    showNotification('Processing your answer...', 'info');
    
    try {
        // Convert blob to base64
        const audioBase64 = await blobToBase64(audioBlob);
        
        // Get current question
        const currentQuestion = appState.currentQuestions[appState.currentQuestionIndex];
        
        // Step 1: Transcribe
        const transcribeResponse = await fetch(`${API_BASE_URL}/interview/transcribe`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                audio_base64: audioBase64.split(',')[1], // Remove data:audio/wav;base64,
                question_id: currentQuestion.question_id
            })
        });
        
        if (!transcribeResponse.ok) {
            throw new Error('Transcription failed');
        }
        
        const transcriptionData = await transcribeResponse.json();
        const transcription = transcriptionData.transcription;
        
        // Display user's answer
        displayUserAnswer(transcription);
        
        // Step 2: Analyze
        const analyzeResponse = await fetch(`${API_BASE_URL}/interview/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                transcription: transcription,
                question_text: currentQuestion.question_text,
                question_id: currentQuestion.question_id
            })
        });
        
        if (!analyzeResponse.ok) {
            throw new Error('Analysis failed');
        }
        
        const analysisData = await analyzeResponse.json();
        
        // Display feedback
        displayFeedback(analysisData);
        
        // Move to next question after a delay
        setTimeout(() => {
            appState.currentQuestionIndex++;
            displayQuestion(appState.currentQuestionIndex);
        }, 3000);
        
    } catch (error) {
        console.error('Error processing audio:', error);
        showNotification('Error processing answer. Please try again.', 'error');
    }
}

function displayUserAnswer(transcription) {
    const chatMessages = document.getElementById('chat-messages');
    
    const answerHTML = `
        <div class="flex gap-4 mb-6 justify-end">
            <div class="flex-1 flex justify-end">
                <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-4 max-w-[80%]">
                    <p class="text-zinc-200 leading-relaxed">${transcription}</p>
                </div>
            </div>
            <div class="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center shrink-0">
                <i data-lucide="user" class="w-5 h-5 text-emerald-400"></i>
            </div>
        </div>
    `;
    
    chatMessages.innerHTML += answerHTML;
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function displayFeedback(analysis) {
    const chatMessages = document.getElementById('chat-messages');
    
    const feedbackHTML = `
        <div class="flex gap-4 mb-6">
            <div class="w-10 h-10 rounded-full bg-indigo-500/10 flex items-center justify-center shrink-0">
                <i data-lucide="sparkles" class="w-5 h-5 text-indigo-400"></i>
            </div>
            <div class="flex-1">
                <div class="text-sm text-zinc-500 mb-2">AI Feedback</div>
                <div class="bg-zinc-900 border border-zinc-800 rounded-2xl p-4 space-y-3">
                    <div class="flex gap-3 text-sm">
                        <span class="text-zinc-400">Overall:</span>
                        <span class="text-emerald-400 font-medium">${analysis.overall_score}/100</span>
                    </div>
                    <div class="grid grid-cols-3 gap-2 text-xs">
                        <div><span class="text-zinc-500">Content:</span> <span class="text-zinc-300">${analysis.content_score}</span></div>
                        <div><span class="text-zinc-500">Clarity:</span> <span class="text-zinc-300">${analysis.clarity_score}</span></div>
                        <div><span class="text-zinc-500">Confidence:</span> <span class="text-zinc-300">${analysis.confidence_score}</span></div>
                    </div>
                    <p class="text-zinc-400 text-sm leading-relaxed">${analysis.detailed_feedback}</p>
                    ${analysis.filler_words.count > 0 ? `
                        <div class="text-xs text-amber-400/80">
                            ⚠️ Filler words detected: ${analysis.filler_words.count} (${analysis.filler_words.percentage}%)
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
    
    chatMessages.innerHTML += feedbackHTML;
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// ==================== Utilities ====================

function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}

function showNotification(message, type = 'info') {
    // Simple console log for now
    // You can implement a toast notification UI later
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Optional: Add a simple alert for errors
    if (type === 'error') {
        // You can add a toast UI here later
    }
}

function showInterviewComplete() {
    const chatMessages = document.getElementById('chat-messages');
    
    const completeHTML = `
        <div class="flex flex-col items-center justify-center p-12 text-center">
            <div class="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center mb-4">
                <i data-lucide="check-circle" class="w-8 h-8 text-emerald-400"></i>
            </div>
            <h3 class="text-xl text-white font-medium mb-2">Interview Complete!</h3>
            <p class="text-zinc-400">Great job! Check your feedback above.</p>
        </div>
    `;
    
    chatMessages.innerHTML += completeHTML;
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// ==================== Initialization ====================

document.addEventListener('DOMContentLoaded', () => {
    // Attach form submit handler
    const mockForm = document.getElementById('mock-form');
    if (mockForm) {
        mockForm.addEventListener('submit', handleMockInterviewSubmit);
    }
    
    // Make recording functions global
    window.startRecording = startRecording;
    window.stopRecording = stopRecording;
});
