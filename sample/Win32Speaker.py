import win32com.client

speaker = win32com.client.Dispatch("SAPI.SpVoice")
speaker.Speak("I'm WangYu. Oh, It works!")
speaker.Speak("我是王宇!")