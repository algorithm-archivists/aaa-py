from src.build import build
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", '-l', help="Use local mode", action="store_true")
    args = parser.parse_args()
    build(args.local)

