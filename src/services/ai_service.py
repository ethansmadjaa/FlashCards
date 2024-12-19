import json
import os
import re
from difflib import SequenceMatcher
from typing import List, Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


class AICardGenerator:
    @staticmethod
    def check_similarity(text1: str, text2: str) -> float:
        """Check similarity between two texts using multiple methods"""
        # Basic cleaning
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()

        # Get word sets
        words1 = set(text1.split())
        words2 = set(text2.split())

        # Calculate Jaccard similarity for word overlap
        jaccard = len(words1.intersection(words2)) / len(words1.union(words2)) if words1 or words2 else 0

        # Calculate sequence similarity
        sequence = SequenceMatcher(None, text1, text2).ratio()

        # Return weighted average
        return (jaccard * 0.5 + sequence * 0.5)

    @staticmethod
    def filter_similar_cards(new_cards: List[Dict], existing_cards: List[Dict],
                             similarity_threshold: float = 0.8) -> tuple[List[Dict], List[Dict]]:
        """Filter out cards that are too similar to existing ones"""
        unique_cards = []
        duplicates = []

        for new_card in new_cards:
            is_duplicate = False
            new_q = new_card['question'].lower().strip()
            new_a = new_card['answer'].lower().strip()

            # Remove punctuation and normalize spaces
            new_q = re.sub(r'[^\w\s]', '', new_q)
            new_a = re.sub(r'[^\w\s]', '', new_a)

            for existing_card in existing_cards:
                existing_q = existing_card['question'].lower().strip()
                existing_a = existing_card['answer'].lower().strip()

                # Clean existing card text
                existing_q = re.sub(r'[^\w\s]', '', existing_q)
                existing_a = re.sub(r'[^\w\s]', '', existing_a)

                # Check question similarity
                question_similarity = AICardGenerator.check_similarity(new_q, existing_q)

                # Check answer similarity
                answer_similarity = AICardGenerator.check_similarity(new_a, existing_a)

                # Consider it a duplicate if either question or answer is too similar
                if question_similarity > similarity_threshold or answer_similarity > similarity_threshold:
                    is_duplicate = True
                    duplicates.append({
                        'new_card': new_card,
                        'existing_card': existing_card,
                        'question_similarity': question_similarity,
                        'answer_similarity': answer_similarity
                    })
                    print(f"\nPotential duplicate found:")
                    print(f"New Q: {new_card['question']}")
                    print(f"Existing Q: {existing_card['question']}")
                    print(f"Question similarity: {question_similarity:.2f}")
                    print(f"Answer similarity: {answer_similarity:.2f}")
                    break

            if not is_duplicate:
                unique_cards.append(new_card)

        return unique_cards, duplicates

    @staticmethod
    def generate_unique_cards(topic: str, num_cards: int, difficulty: str = "mixed",
                              existing_cards: List[Dict] = None) -> tuple[List[Dict], int]:
        """Generate cards and filter out duplicates"""
        # First, generate the requested number of cards
        new_cards = AICardGenerator.generate_cards(topic, num_cards, difficulty)

        if not new_cards:
            return [], 0

        if existing_cards:
            # Filter existing cards for the same class
            class_cards = [card for card in existing_cards
                           if card.get('class_name') == topic]

            # Filter out similar cards
            unique_cards, duplicates = AICardGenerator.filter_similar_cards(
                new_cards, class_cards
            )

            duplicate_count = len(duplicates)

            # Print duplicate information
            if duplicate_count > 0:
                print(f"\nFound {duplicate_count} similar cards:")
                for dup in duplicates:
                    print(f"\nNew question: {dup['new_card']['question']}")
                    print(f"Similar to existing: {dup['existing_card']['question']}")
                    print(f"Similarity: {dup['similarity']:.2f}")

            return unique_cards, duplicate_count

        return new_cards, 0

    @staticmethod
    def generate_cards(topic: str, num_cards: int, difficulty: str = "mixed") -> List[Dict]:
        """Generate flashcards using OpenAI API"""
        prompt = f"""Generate EXACTLY {num_cards} flashcards about {topic}.
        
        IMPORTANT FORMAT RULES:
        1. Use ONLY ASCII characters (no accents or special characters)
        2. The class_name field must ONLY contain the topic name: "{topic}"
        3. Keep answers concise (max 200 characters)
        4. Each card must follow this EXACT format:
        {{
            "question": "Question text here",
            "answer": "Brief answer here",
            "class_name": "{topic}",
            "difficulty": "{difficulty}"
        }}

        Required:
        - Generate exactly {num_cards} cards
        - Each card must have all 4 fields
        - No trailing commas in JSON
        - Return only a valid JSON array of cards
        - Questions must be unique
        - Answers must be clear but brief

        Return the array starting with [ and ending with ], no other text."""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a JSON generator that creates flashcards in strict JSON format. Always validate your JSON before responding."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            content = response.choices[0].message.content.strip()

            # Debug logging
            print("Received content from API:")
            print(content)

            try:
                # Parse and validate JSON
                cards = json.loads(content)

                # Validate it's a list
                if not isinstance(cards, list):
                    raise ValueError("Response is not a JSON array")

                # Validate card count
                if len(cards) != num_cards:
                    raise ValueError(f"Generated {len(cards)} cards instead of requested {num_cards}")

                # Validate each card
                valid_cards = []
                seen_questions = set()  # To check for duplicates

                for i, card in enumerate(cards):
                    # Check required fields
                    required_fields = ["question", "answer", "class_name", "difficulty"]
                    if not all(key in card for key in required_fields):
                        print(f"Card {i} missing required fields: {card}")
                        continue

                    # Check for empty fields
                    if any(not str(card[key]).strip() for key in required_fields):
                        print(f"Card {i} has empty fields: {card}")
                        continue

                    # Check for duplicate questions
                    question = card["question"].strip().lower()
                    if question in seen_questions:
                        print(f"Card {i} has duplicate question: {question}")
                        continue

                    seen_questions.add(question)

                    # Force correct class_name and difficulty
                    card["class_name"] = topic
                    card["difficulty"] = difficulty

                    valid_cards.append(card)

                # Final count validation
                if len(valid_cards) != num_cards:
                    raise ValueError(f"Only {len(valid_cards)} valid cards out of {num_cards} requested")

                print(f"Successfully validated all {len(valid_cards)} cards")
                return valid_cards

            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print("Invalid JSON content received:", content)
                return []
            except ValueError as e:
                print(f"Validation error: {e}")
                return []

        except Exception as e:
            print(f"API or other error: {e}")
            return []
