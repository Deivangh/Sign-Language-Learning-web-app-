import streamlit as st
import pytesseract
from PIL import Image
import os
import re
import base64
import json
import cv2
import mediapipe as mp

st.set_page_config(layout="centered")
st.title("Sign Language Learning System")

# ---------- SESSION STATE ----------
if "gesture_trigger" not in st.session_state:
    st.session_state.gesture_trigger = 0

if "last_gesture" not in st.session_state:
    st.session_state.last_gesture = None

# ---------- MEDIAPIPE ----------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# ---------- LIVE GESTURE DETECTION ----------
def detect_gesture_live():
    cap = cv2.VideoCapture(0)
    stframe = st.empty()
    last_action = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        action = None

                    # ---------- GESTURE DETECTION ----------
        if result.multi_hand_landmarks:
            for handLms in result.multi_hand_landmarks:
        
                mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
        
                lm = handLms.landmark
        
                # Finger tips
                thumb_tip = lm[4]
                thumb_ip = lm[3]
        
                index_tip = lm[8]
                index_pip = lm[6]
        
                middle_tip = lm[12]
                middle_pip = lm[10]
        
                ring_tip = lm[16]
                ring_pip = lm[14]
        
                pinky_tip = lm[20]
                pinky_pip = lm[18]
        
                # ---------- REPEAT ----------
                # Open palm → all fingers up
                if (
                    index_tip.y < index_pip.y and
                    middle_tip.y < middle_pip.y and
                    ring_tip.y < ring_pip.y and
                    pinky_tip.y < pinky_pip.y
                ):
                    action = "repeat"
        
                # ---------- GOOD ----------
                # Thumb up only
                elif (
                    thumb_tip.y < thumb_ip.y and
                    index_tip.y > index_pip.y and
                    middle_tip.y > middle_pip.y
                ):
                    action = "good"
        
                # ---------- STOP ----------
                else:
                    action = "stop"

        stframe.image(frame, channels="BGR")

        if action and action != last_action:
            cap.release()
            return action

    cap.release()
    return None

# ---------- LOAD AVATAR ----------
avatar_base64 = ""
if os.path.exists("avatar.glb"):
    with open("avatar.glb", "rb") as f:
        avatar_base64 = base64.b64encode(f.read()).decode()

# ---------- LOAD POSE ----------
def load_pose(word):
    pose_path = os.path.join("poses", f"{word}_pose.json")
    if os.path.exists(pose_path):
        with open(pose_path, "r") as f:
            return json.load(f)
    return None

# ---------- UI ----------
uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

# ---------- LIVE CAMERA ----------
if st.checkbox("Start Gesture Control"):

    gesture = detect_gesture_live()

    if gesture:
        st.session_state.gesture_trigger += 1
        st.session_state.last_gesture = gesture
        st.success(f"Detected Gesture: {gesture}")

# ---------- MAIN ----------
if uploaded_file:

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # OCR
    text = pytesseract.image_to_string(image)
    st.write("Extracted Text:", text)

    # WORD CLEANING
    words = re.findall(r'\b\w+\b', text.lower())

    # ---------- GESTURE ACTION ----------
    if st.session_state.last_gesture == "repeat":
        st.info("Repeating sentence")

    elif st.session_state.last_gesture == "good":
        st.info("Showing Thank You")
        words = ["thankyou"]

    elif st.session_state.last_gesture == "stop":
        st.warning("Stopped")
        words = []

    video_dir = "videos"
    matched_videos = []
    matched_words = []
    pose_words = []

    for word in words:

        pose = load_pose(word)
        if pose:
            pose_words.append(word)

        video_path = os.path.join(video_dir, f"{word}.mp4")
        if os.path.exists(video_path):
            with open(video_path, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()

            matched_videos.append(f"data:video/mp4;base64,{b64}")
            matched_words.append(word)

    # ---------- AVATAR ----------
    if pose_words and avatar_base64 != "":
    
        word_to_animate = pose_words[0]
        pose_file = f"poses/{word_to_animate}_pose.json"
    
        avatar_html = f"""
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    
        <div id="avatarContainer_{st.session_state.gesture_trigger}"
             style="width:100%; height:700px;"></div>
    
        <script>
    
        // ---------- SCENE ----------
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xeeeeee);
    
        // ---------- CAMERA ----------
        const camera = new THREE.PerspectiveCamera(
            45,
            window.innerWidth / 700,
            0.1,
            1000
        );
    
        camera.position.set(0, 1, 5);
    
        // ---------- RENDERER ----------
        const renderer = new THREE.WebGLRenderer({{ antialias:true }});
        renderer.setSize(window.innerWidth * 0.8, 700);
    
        document.getElementById(
            'avatarContainer_{st.session_state.gesture_trigger}'
        ).appendChild(renderer.domElement);
    
        // ---------- LIGHTS ----------
        const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 2);
        scene.add(hemiLight);
    
        const dirLight = new THREE.DirectionalLight(0xffffff, 1);
        dirLight.position.set(0, 10, 10);
        scene.add(dirLight);
    
        // ---------- GRID ----------
        
    
        // ---------- LOADER ----------
        const loader = new THREE.GLTFLoader();
    
        let avatar;
        let poseData = [];
        let frame = 0;
    
        loader.load(
            "data:model/gltf-binary;base64,{avatar_base64}",
    
            function(gltf) {{
    
                avatar = gltf.scene;
    
                scene.add(avatar);
                
                avatar.traverse(function(obj) {{
    if (obj.isMesh) {{
        obj.frustumCulled = false;
    }}
}});
    
                // ---------- AVATAR POSITION ----------
                avatar.position.set(0, -2, 0);

    
                // ---------- SCALE ----------
                avatar.scale.set(1.2,1.2,1.2);
    
                console.log(avatar);
    
                // ---------- LOAD POSE ----------
                fetch("{pose_file}")
                .then(res => res.json())
                .then(data => {{
                    poseData = data;
                    console.log("Pose Loaded");
                }});
    
            }}
        );
    
        // ---------- APPLY POSE ----------
        function applyPose(frameData) {{
    
            if(!avatar || !frameData) return;
    
            // ---------- RIGHT HAND ----------
            if(frameData.right_hand) {{
    
                const rightHand =
                    avatar.getObjectByName("mixamorig7:RightHand");
    
                if(rightHand) {{
    
                    rightHand.rotation.x =
                        frameData.right_hand[0][0] * 3;
    
                    rightHand.rotation.y =
                        frameData.right_hand[0][1] * 3;
    
                    rightHand.rotation.z =
                        frameData.right_hand[0][2] * 3;
                }}
            }}
    
            // ---------- LEFT HAND ----------
            if(frameData.left_hand) {{
    
                const leftHand =
                    avatar.getObjectByName("mixamorig7:LeftHand");
    
                if(leftHand) {{
    
                    leftHand.rotation.x =
                        frameData.left_hand[0][0] * 3;
    
                    leftHand.rotation.y =
                        frameData.left_hand[0][1] * 3;
    
                    leftHand.rotation.z =
                        frameData.left_hand[0][2] * 3;
                }}
            }}
    
            // ---------- BODY MOVEMENT ----------
            const spine =
                avatar.getObjectByName("mixamorig7:Spine");
    
            if(spine) {{
                spine.rotation.z = Math.sin(frame * 0.05) * 0.1;
            }}
    
            // ---------- HEAD MOVEMENT ----------
            const head =
                avatar.getObjectByName("mixamorig7:Head");
    
            if(head) {{
                head.rotation.y = Math.sin(frame * 0.03) * 0.2;
            }}
    
            // ---------- ARM MOVEMENT ----------
            const leftArm =
                avatar.getObjectByName("mixamorig7:LeftArm");
    
            const rightArm =
                avatar.getObjectByName("mixamorig7:RightArm");
    
            if(leftArm) {{
                leftArm.rotation.x = Math.sin(frame * 0.05) * 0.2;
            }}
    
            if(rightArm) {{
                rightArm.rotation.x = Math.sin(frame * 0.05) * 0.2;
            }}
        }}
    
        // ---------- ANIMATION ----------
        function animate() {{
    
            requestAnimationFrame(animate);
    
            if(poseData.length > 0) {{
    
                if(frame >= poseData.length) {{
                    frame = 0;
                }}
    
                applyPose(poseData[frame]);
    
                frame++;
            }}
    
            renderer.render(scene, camera);
        }}
    
        animate();
    
        </script>
        """
    
        st.components.v1.html(avatar_html, height=750)

    # ---------- VIDEO ----------
    if matched_videos:

        st.write("Found Videos for:", matched_words)

        unique_id = st.session_state.gesture_trigger
        video_tags = str(matched_videos).replace("'", '"')

        autoplay_html = f"""
        <video id="videoPlayer_{unique_id}" width="640" height="480" controls autoplay></video>

        <script>
            const videos = {video_tags};
            let current = 0;
            const player = document.getElementById('videoPlayer_{unique_id}');

            function playNext() {{
                if (current < videos.length) {{
                    player.src = videos[current];
                    player.load();
                    player.play();
                    current++;
                }}
            }}

            player.onended = playNext;
            playNext();
        </script>
        """

        st.components.v1.html(autoplay_html, height=500)

    else:
        st.warning("No matching sign language videos found.")