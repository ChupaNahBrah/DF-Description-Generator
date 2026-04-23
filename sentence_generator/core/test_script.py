from .generator import load_data, generate_sentence

# ─────────────────────────────────────
# Generate and print multiple sentences
# ─────────────────────────────────────
def run_tests():
    """
    Load required data and generate 5 example sentences.
    Each sentence is printed on its own line with spacing.
    """
    load_data()  # Initialize subjects, descriptions, weights

    for _ in range(5):
        sentence = generate_sentence()
        print(sentence + "\n")  # Add a blank line for separation


# ─────────────────────────────────────
# Main script entry point
# ─────────────────────────────────────
if __name__ == "__main__":
    run_tests()