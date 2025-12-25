import whisper

model = whisper.load_model("large")  # start with base

result = model.transcribe("audios/admissions:17163790335111cz9l9mn1_20251223_103929.wav", language="fr")

print("Transcription:")
print(result["text"])
