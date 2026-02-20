from rvc_python.infer import VoiceClone
import os

# Initialize the RVC model globally so it doesn't reload on every request
rvc_cloner = None
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'mahiru')

def init_rvc():
    global rvc_cloner
    try:
        model_path = os.path.join(MODEL_DIR, "MahiruShiina.pth")
        index_path = os.path.join(MODEL_DIR, "mahiru.index")
        
        if os.path.exists(model_path):
            rvc_cloner = VoiceClone()
            print(f"Loading RVC Model from {model_path}...")
            # Load the model. Using f0_method 'rmvpe' which is the default high-quality method
            rvc_cloner.load_model(model_path)
            print("RVC Model loaded successfully!")
            
            # Note: rvc_python might not natively support setting index path in load_model directly depending on version, 
            # we will pass it during inference.
            return True
        else:
            print(f"RVC Model file not found at {model_path}")
            return False
            
    except Exception as e:
        print(f"Error initializing RVC: {e}")
        return False

def convert_voice(input_audio_path, output_audio_path):
    global rvc_cloner
    if rvc_cloner is None:
        raise Exception("RVC Model is not initialized.")
        
    try:
        index_path = os.path.join(MODEL_DIR, "mahiru.index")
        
        # Perform inference
        rvc_cloner.infer(
            input_path=input_audio_path,
            output_path=output_audio_path,
            f0_method="rmvpe", # best vocal extraction method
            f0_up_key=0,       # pitch shift (0 for same pitch, Mahiru is female so 0 if input is female Hoai My)
            index_path=index_path if os.path.exists(index_path) else None,
            index_rate=0.75,
            filter_radius=3,
            rms_mix_rate=0.25,
            protect=0.33
        )
        return True
    except Exception as e:
        print(f"Voice conversion failed: {e}")
        raise e
