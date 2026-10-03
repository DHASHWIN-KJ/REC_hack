"""
src/video/cli.py
Command-line interface for the Video Deepfake Detection pipeline.
"""
import argparse
import sys
import json
from pathlib import Path

# Absolute imports inside the package
from video.schemas import EvidenceBundle

def analyze_video_cmd(video_path: str, output_path: str = None):
    """
    Analyzes a video using the full detection pipeline.
    """
    path = Path(video_path)
    if not path.exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
        
    print(f"Analyzing {path.name}...")
    
    # Import here to avoid loading heavy torch libraries for fast CLI help
    from video.pipeline import VideoAnalyzer
    
    try:
        analyzer = VideoAnalyzer()
        bundle = analyzer.analyze_video(path)
    except Exception as e:
        print(f"Failed to analyze video: {e}")
        sys.exit(1)
    
    result_json = bundle.model_dump_json(indent=2)
    
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result_json)
        print(f"Saved results to {output_path}")
    else:
        print(result_json)


def main():
    parser = argparse.ArgumentParser(description="Video Deepfake Detection CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analyze command
    parser_analyze = subparsers.add_parser("analyze", help="Analyze a single video file")
    parser_analyze.add_argument("video_path", type=str, help="Path to the input video")
    parser_analyze.add_argument("--out", type=str, default=None, help="Path to save JSON output")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        analyze_video_cmd(args.video_path, args.out)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
