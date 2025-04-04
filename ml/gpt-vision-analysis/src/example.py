from pathlib import Path

from rich import print
from rich.console import Console
from rich.panel import Panel
from vision_analyzer import VisionAnalyzer


def main():
    console = Console()

    try:
        # Initialize the analyzer
        analyzer = VisionAnalyzer()

        # Example image path - you should replace this with your image
        image_path = Path("data/sample_images/example.png")

        # Analysis prompt
        prompt = """Please analyze this image in detail. Include:
        1. Main subjects/objects
        2. Colors and composition
        3. Mood or atmosphere
        4. Any notable details or unusual elements"""

        console.print(Panel.fit(
            "[yellow]Analyzing image...[/yellow]",
            title="GPT Vision Analysis"
        ))

        # Perform analysis
        result = analyzer.analyze_image(image_path, prompt)

        # Print results
        console.print("\n[green]Analysis Results:[/green]")
        console.print(Panel(
            result.analysis,
            title="GPT-4 Vision Analysis",
            subtitle=f"Model: {result.model_used} | Time: {result.processing_time:.2f}s"
        ))

    except Exception as e:
        console.print(f"[red]Error:[/red] {e!s}")


if __name__ == "__main__":
    main()
