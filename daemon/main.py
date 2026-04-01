"""Entry point for dev-tracker daemon."""
import sys
from daemon.tracker import ActivityTracker
from daemon import exporter


def main():
    """Main function to start the tracker."""
    # Export any unsynced sessions before starting
    try:
        exporter.run()
    except Exception as e:
        print(f"Export error (non-critical): {e}", file=sys.stderr)
    
    # Configuration parameters
    POLL_INTERVAL = 5  # seconds
    IDLE_THRESHOLD = 120  # seconds (2 minutes)
    
    tracker = ActivityTracker(
        poll_interval=POLL_INTERVAL,
        idle_threshold=IDLE_THRESHOLD
    )
    
    try:
        tracker.start()
    except Exception as e:
        print(f"Critical error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
