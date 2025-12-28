"""
Audio recorder component with pause/resume functionality
"""
import streamlit.components.v1 as components


def audio_recorder_component():
    """
    Custom audio recorder with pause/resume that looks like st.audio_input
    Returns audio bytes when recording is stopped
    """
    
    component_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .recorder-wrapper {
                display: flex;
                flex-direction: column;
                gap: 8px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            
            .main-button {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                padding: 8px 16px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.2s;
            }
            
            .main-button:hover {
                background: #5568d3;
                transform: translateY(-1px);
            }
            
            .main-button.recording {
                background: #e74c3c;
            }
            
            .main-button.recording:hover {
                background: #c0392b;
            }
            
            .control-buttons {
                display: flex;
                gap: 8px;
            }
            
            .control-btn {
                flex: 1;
                padding: 6px 12px;
                border: 1px solid #ddd;
                background: white;
                border-radius: 6px;
                cursor: pointer;
                font-size: 13px;
                transition: all 0.2s;
            }
            
            .control-btn:hover:not(:disabled) {
                background: #f0f0f0;
                border-color: #999;
            }
            
            .control-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .timer {
                text-align: center;
                font-size: 16px;
                font-weight: 600;
                color: #333;
                font-variant-numeric: tabular-nums;
            }
            
            .status {
                text-align: center;
                font-size: 12px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="recorder-wrapper">
            <button id="mainBtn" class="main-button">
                <span id="icon">🎤</span>
                <span id="mainText">Click to record</span>
            </button>
            
            <div id="controls" class="control-buttons" style="display: none;">
                <button id="pauseBtn" class="control-btn">⏸️ Pause</button>
                <button id="resumeBtn" class="control-btn" style="display: none;">▶️ Resume</button>
                <button id="stopBtn" class="control-btn">⏹️ Stop</button>
            </div>
            
            <div id="timer" class="timer" style="display: none;">00:00</div>
            <div id="status" class="status"></div>
        </div>

        <script>
            let mediaRecorder;
            let audioChunks = [];
            let startTime;
            let pausedTime = 0;
            let timerInterval;
            let stream;
            
            const mainBtn = document.getElementById('mainBtn');
            const icon = document.getElementById('icon');
            const mainText = document.getElementById('mainText');
            const controls = document.getElementById('controls');
            const pauseBtn = document.getElementById('pauseBtn');
            const resumeBtn = document.getElementById('resumeBtn');
            const stopBtn = document.getElementById('stopBtn');
            const timer = document.getElementById('timer');
            const status = document.getElementById('status');
            
            function updateTimer() {
                const elapsed = Date.now() - startTime - pausedTime;
                const totalSeconds = Math.floor(elapsed / 1000);
                const minutes = Math.floor(totalSeconds / 60);
                const seconds = totalSeconds % 60;
                timer.textContent = String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
            }
            
            function sendToStreamlit(audioData) {
                if (window.parent && window.parent.streamlitSetComponentValue) {
                    window.parent.streamlitSetComponentValue(audioData);
                }
            }
            
            mainBtn.addEventListener('click', async () => {
                try {
                    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = (e) => {
                        if (e.data.size > 0) audioChunks.push(e.data);
                    };
                    
                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        const reader = new FileReader();
                        reader.onloadend = () => {
                            const base64 = reader.result.split(',')[1];
                            sendToStreamlit(base64);
                            status.textContent = 'Recording saved!';
                        };
                        reader.readAsDataURL(audioBlob);
                        
                        stream.getTracks().forEach(track => track.stop());
                        
                        // Reset UI
                        mainBtn.classList.remove('recording');
                        icon.textContent = '🎤';
                        mainText.textContent = 'Click to record';
                        controls.style.display = 'none';
                        timer.style.display = 'none';
                        timer.textContent = '00:00';
                    };
                    
                    mediaRecorder.start();
                    startTime = Date.now();
                    pausedTime = 0;
                    timerInterval = setInterval(updateTimer, 100);
                    
                    // Update UI
                    mainBtn.classList.add('recording');
                    icon.textContent = '🔴';
                    mainText.textContent = 'Recording...';
                    controls.style.display = 'flex';
                    timer.style.display = 'block';
                    pauseBtn.style.display = 'block';
                    resumeBtn.style.display = 'none';
                    status.textContent = '';
                    
                } catch (err) {
                    status.textContent = 'Microphone access denied';
                    console.error(err);
                }
            });
            
            pauseBtn.addEventListener('click', () => {
                if (mediaRecorder && mediaRecorder.state === 'recording') {
                    mediaRecorder.pause();
                    const pauseStart = Date.now();
                    pauseBtn.dataset.pauseStart = pauseStart;
                    
                    clearInterval(timerInterval);
                    
                    pauseBtn.style.display = 'none';
                    resumeBtn.style.display = 'block';
                    icon.textContent = '⏸️';
                    mainText.textContent = 'Paused';
                    mainBtn.classList.remove('recording');
                    status.textContent = 'Recording paused';
                }
            });
            
            resumeBtn.addEventListener('click', () => {
                if (mediaRecorder && mediaRecorder.state === 'paused') {
                    const pauseStart = parseInt(pauseBtn.dataset.pauseStart);
                    pausedTime += Date.now() - pauseStart;
                    
                    mediaRecorder.resume();
                    timerInterval = setInterval(updateTimer, 100);
                    
                    resumeBtn.style.display = 'none';
                    pauseBtn.style.display = 'block';
                    icon.textContent = '🔴';
                    mainText.textContent = 'Recording...';
                    mainBtn.classList.add('recording');
                    status.textContent = '';
                }
            });
            
            stopBtn.addEventListener('click', () => {
                if (mediaRecorder) {
                    mediaRecorder.stop();
                    clearInterval(timerInterval);
                    status.textContent = 'Processing...';
                }
            });
        </script>
    </body>
    </html>
    """
    
    return components.html(component_html, height=120)