import cv2
import mediapipe as mp
import grpc
import hand_pb2
import hand_pb2_grpc

def run_detection_service():
    # --- gRPC Client Setup ---
    # Connect to the tracking service (Service 2) running on port 50051
    channel = grpc.insecure_channel('localhost:50051')
    stub = hand_pb2_grpc.HandProcessorStub(channel)

    # --- MediaPipe Setup ---
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    # --- Webcam Setup ---
    cap = cv2.VideoCapture(0)

    print("Detection Service Started. Press ESC to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip for mirror view
        frame = cv2.flip(frame, 1)

        # Convert to RGB for MediaPipe processing
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks,
                results.multi_handedness
            ):
                # Filter only the RIGHT hand
                label = handedness.classification[0].label
                if label != "Right":
                    continue

                # Get index finger tip landmarks (Point 8)
                index_tip = hand_landmarks.landmark[8]
                
                # --- Send Data via gRPC ---
                try:
                    # Send normalized x and y coordinates (0.0 to 1.0)
                    stub.SendPosition(hand_pb2.PositionRequest(
                        x=index_tip.x, 
                        y=index_tip.y
                    ))
                except grpc.RpcError:
                    # Log error if Service 2 is not reachable
                    pass

                # Draw landmarks for visual feedback
                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

                # Convert normalized coordinates to pixel coordinates for display
                h, w, _ = frame.shape
                cx, cy = int(index_tip.x * w), int(index_tip.y * h)

                # Draw a circle on the index tip
                cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

                # Display coordinates on the screen
                cv2.putText(frame, f"Right Hand Sent ({index_tip.x:.2f},{index_tip.y:.2f})",
                            (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2)

        # Show the result
        cv2.imshow("Hand Detection Service (gRPC Client)", frame)

        # Exit on ESC key
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_detection_service()