import json
from collections import defaultdict


def clean_flashcards():
    # Load the flashcards
    with open('flashcards.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)

    # Create a dictionary to store unique cards
    unique_cards = defaultdict(list)
    duplicates = []

    # Group cards by question (case-insensitive)
    for card in cards:
        question_key = card['question'].lower().strip()
        unique_cards[question_key].append(card)

    # Find and print duplicates
    print("\nChecking for duplicates...")
    duplicate_count = 0
    cleaned_cards = []

    for question, card_list in unique_cards.items():
        if len(card_list) > 1:
            duplicate_count += 1
            print(f"\nDuplicate found ({len(card_list)} occurrences):")
            print(f"Question: {card_list[0]['question']}")
            print("Classes:", [card['class_name'] for card in card_list])
            duplicates.extend(card_list[1:])
        # Keep only the first occurrence
        cleaned_cards.append(card_list[0])

    # Save cleaned cards
    if duplicate_count > 0:
        print(f"\nFound {duplicate_count} duplicate questions")
        print(f"Original card count: {len(cards)}")
        print(f"Cleaned card count: {len(cleaned_cards)}")

        # Save cleaned cards
        with open('flashcards_cleaned.json', 'w', encoding='utf-8') as f:
            json.dump(cleaned_cards, f, indent=2)

        print("\nCleaned cards saved to 'flashcards_cleaned.json'")
        print("Please review the cleaned file and replace the original if satisfied.")
    else:
        print("No duplicates found!")


if __name__ == "__main__":
    clean_flashcards()
