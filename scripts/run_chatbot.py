#!/usr/bin/env python3
"""
Run RAG Chatbot CLI

Interactive chatbot for Viaggiare Bucarest tour assistance.

Usage:
    python3 scripts/run_chatbot.py              # Interactive mode
    python3 scripts/run_chatbot.py --test       # Test mode with synthetic questions
"""

import sys
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.chatbot import TourChatbot


def test_chatbot(questions: List[str]):
    """
    Test chatbot with synthetic questions.

    Args:
        questions: List of Italian questions to test
    """
    print("=" * 70)
    print("🧪 TESTING CHATBOT WITH SYNTHETIC QUESTIONS")
    print("=" * 70)

    try:
        chatbot = TourChatbot()

        for i, question in enumerate(questions, 1):
            print(f"\n{'='*70}")
            print(f"TEST {i}/{len(questions)}")
            print(f"{'='*70}")
            print(f"💬 Domanda: {question}")
            print()

            result = chatbot.chat(question, show_context=False)

            print(f"🤖 Risposta:\n{result['answer']}")
            print(f"\n📚 Fonti utilizzate: {', '.join(result['sources'][:3])}")

        print(f"\n{'='*70}")
        print("✅ Test completato!")
        print(f"{'='*70}\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Test mode with synthetic questions
        test_questions = [
            "Quanto costa il tour del Parlamento?",
            "Come posso contattare Viaggiare Bucarest?",
            "Raccontami del tour al Castello di Dracula e la riserva degli orsi"
        ]
        test_chatbot(test_questions)
    else:
        # Interactive mode
        try:
            chatbot = TourChatbot()
            chatbot.run_interactive()
        except FileNotFoundError as e:
            print(f"\n❌ Error: {e}")
            print("Please run: python3 scripts/build_index.py first")
            sys.exit(1)
        except ValueError as e:
            print(f"\n❌ Error: {e}")
            print("Please check your .env file contains DEEPSEEK_API_KEY")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
