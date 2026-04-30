import grpc
from concurrent import futures
import hand_pb2
import hand_pb2_grpc
import redis
import os

# --- Configuration ---
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_KEY = "aim_direction"

class HandTrackingServicer(hand_pb2_grpc.HandProcessorServicer):
    def __init__(self):
        # Initialize Redis connection
        self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        
        # Store the previous position to calculate direction
        self.prev_x = None
        self.prev_y = None
        
        # Sensitivity threshold (to avoid jitter)
        self.threshold = 0.02 

    def SendPosition(self, request, context):
        current_x = request.x
        current_y = request.y

        if self.prev_x is not None and self.prev_y is not None:
            dx = current_x - self.prev_x
            dy = current_y - self.prev_y

            direction = ""

            # Determine Horizontal Direction
            if abs(dx) > abs(dy):
                if dx > self.threshold:
                    direction = "RIGHT"
                elif dx < -self.threshold:
                    direction = "LEFT"
            # Determine Vertical Direction
            else:
                if dy > self.threshold:
                    direction = "DOWN" # In computer vision, Y increases downwards
                elif dy < -self.threshold:
                    direction = "UP"

            if direction:
                # Send to Redis
                self.redis_client.set(REDIS_KEY, direction)
                print(f"Movement Detected: {direction}")

        # Update previous coordinates
        self.prev_x = current_x
        self.prev_y = current_y
        
        return hand_pb2.EmptyResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hand_pb2_grpc.add_HandProcessorServicer_to_server(HandTrackingServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Tracking Service (gRPC Server) started on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()