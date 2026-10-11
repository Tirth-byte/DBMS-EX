"""Run the complete experiment from the project root."""
from src.generate_data import main as generate
from src.database import main as initialise
from src.benchmark import run_benchmarks
from src.visualize import create_chart

if __name__ == "__main__":
    generate()
    initialise()
    run_benchmarks()
    create_chart()

