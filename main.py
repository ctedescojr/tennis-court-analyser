from utils import read_video, save_video
from trackers import PlayerTracker, BallTracker
from court_line_detector import CourtLineDetector
import cv2


def main():
    # PATHs
    input_video_path = "input_videos/input_video.mp4"
    output_video_path = "output_videos/output_video.avi"
    stub_player_path = "tracker_stubs/player_detections.pkl"
    stub_ball_path = "tracker_stubs/ball_detections.pkl"
    court_model_path = "models/keypoints_model.pth"

    # Read video
    video_frames = read_video(input_video_path)

    # Detect players and ball
    player_tracker = PlayerTracker(model_path="yolov8x")
    player_detections = player_tracker.detect_frames(
        video_frames, read_from_stub=True, stub_path=stub_player_path
    )
    ball_tracker = BallTracker(model_path="models/yolo5_last.pt")
    ball_detections = ball_tracker.detect_frames(
        video_frames, read_from_stub=True, stub_path=stub_ball_path
    )
    ball_detections = ball_tracker.interpolate_ball_positions(ball_detections)

    # Court line detector model
    court_line_detector = CourtLineDetector(court_model_path)
    court_keypoints = court_line_detector.predict(video_frames[0])

    # Choose players
    player_detections = player_tracker.choose_and_filter_players(
        court_keypoints, player_detections
    )

    # Draw output
    ## Draw player bounding boxes
    output_video_frames = player_tracker.draw_bboxes(video_frames, player_detections)
    output_video_frames = ball_tracker.draw_bboxes(output_video_frames, ball_detections)

    ## Draw court keypoints
    output_video_frames = court_line_detector.draw_keypoints_on_video(
        output_video_frames, court_keypoints
    )

    ## Draw frame number on top left corner
    for i, frame in enumerate(output_video_frames):
        cv2.putText(
            frame, f"Frame: {i}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 225, 0), 2
        )

    # Save video
    save_video(output_video_frames, output_video_path)


if __name__ == "__main__":
    main()
