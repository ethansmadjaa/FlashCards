import json


def analyze_question_difficulty(question: str, answer: str) -> str:
    # Keywords indicating complexity
    hard_keywords = ['difference between', 'how does', 'why is', 'explain', 'compare',
                     'analyze', 'evaluate', 'relationship', 'complex', 'technical',
                     'versus', 'vs', 'what is the difference']

    medium_keywords = ['what is the purpose', 'what are', 'how do', 'describe',
                       'function', 'role', 'types', 'components', 'what does',
                       'how is', 'what type']

    # Count words in question and answer
    question_words = len(question.split())
    answer_words = len(answer.split())

    # Check for complexity indicators
    has_hard_keywords = any(kw in question.lower() for kw in hard_keywords)
    has_medium_keywords = any(kw in question.lower() for kw in medium_keywords)

    # Decision logic
    if (has_hard_keywords or
            answer_words > 40 or
            'compare' in question.lower() or
            'difference' in question.lower()):
        return 'hard'
    elif (has_medium_keywords or
          answer_words > 25 or
          question_words > 10):
        return 'medium'
    else:
        return 'easy'


def verify_difficulties():
    try:
        # Load cards
        with open('flashcards.json', 'r', encoding='utf-8') as f_cards:
            flash_cards = json.load(f_cards)

        # Check each card
        total_cards = len(flash_cards)
        cards_with_difficulty = 0
        card_difficulties = {'easy': 0, 'medium': 0, 'hard': 0}
        cards_without_difficulty = []

        for i, flash_card in enumerate(flash_cards):
            if 'difficulty' in flash_card:
                cards_with_difficulty += 1
                card_difficulties[flash_card['difficulty']] += 1
            else:
                cards_without_difficulty.append(f"Card {i}: {flash_card['question'][:50]}...")

        # Print results
        print(f"\nTotal cards: {total_cards}")
        print(f"Cards with difficulty: {cards_with_difficulty}")
        print(f"Cards missing difficulty: {total_cards - cards_with_difficulty}")

        if cards_with_difficulty > 0:
            print("\nDifficulty Distribution:")
            # noinspection PyShadowingNames
            for diff, count in difficulties.items():
                card_percentage = (count / total_cards) * 100
                print(f"{diff.capitalize()}: {count} cards ({card_percentage:.1f}%)")

        if cards_without_difficulty:
            print("\nCards missing difficulty:")
            for flash_card in cards_without_difficulty:
                print(flash_card)

    except Exception as card_e:
        print(f"Error: {card_e}")


try:
    # Load cards
    with open('flashcards.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)

    # Analyze and assign difficulty
    for card in cards:
        card['difficulty'] = analyze_question_difficulty(card['question'], card['answer'])

    # Save updated cards
    with open('flashcards.json', 'w', encoding='utf-8') as f:
        json.dump(cards, f, indent=2)

    # Print statistics
    difficulties = {'easy': 0, 'medium': 0, 'hard': 0}
    for card in cards:
        difficulties[card['difficulty']] += 1

    print("\nDifficulty Distribution:")
    total = len(cards)
    for diff, count in difficulties.items():
        percentage = (count / total) * 100
        print(f"{diff.capitalize()}: {count} cards ({percentage:.1f}%)")

    # Print some examples for verification
    print("\nExample classifications:")
    for difficulty in ['easy', 'medium', 'hard']:
        print(f"\n{difficulty.upper()} question example:")
        example = next(card for card in cards if card['difficulty'] == difficulty)
        print(f"Q: {example['question']}")
        print(f"A: {example['answer']}")
    verify_difficulties()

except Exception as e:
    print(f"Error: {e}")
