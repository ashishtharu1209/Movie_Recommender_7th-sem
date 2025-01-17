import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report

def evaluate_recommendation_system(input_movie, system_recommendations, ground_truth):
    """
    Evaluates a recommendation system and visualizes results graphically.
    
    Args:
        input_movie (str): The movie name used as input.
        system_recommendations (list): Movies recommended by the system.
        ground_truth (list): Actual relevant movies (ground truth).
    
    Returns:
        None: Displays confusion matrix, accuracy, and classification report visually.
    """
    # Get all unique movies from ground truth and recommendations
    all_movies = list(set(system_recommendations + ground_truth))
    
    # Create binary vectors
    y_true = [1 if movie in ground_truth else 0 for movie in all_movies]
    y_pred = [1 if movie in system_recommendations else 0 for movie in all_movies]
    
    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    accuracy = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, output_dict=True)

    # Plot the confusion matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Not Relevant", "Relevant"], yticklabels=["Not Relevant", "Relevant"])
    plt.title(f"Confusion Matrix for '{input_movie}'")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()

    # Display accuracy
    plt.figure(figsize=(6, 4))
    plt.bar(["Accuracy"], [accuracy], color="green")
    plt.ylim(0, 1)
    plt.title("Accuracy Score")
    plt.ylabel("Score")
    plt.text(0, accuracy + 0.02, f"{accuracy:.2f}", ha="center", fontsize=12)
    plt.show()

    # Display classification report as a table
    plt.figure(figsize=(8, 4))
    sns.heatmap(pd.DataFrame(report).iloc[:-1, :].T, annot=True, cmap="YlGnBu", fmt=".2f", cbar=False)
    plt.title("Classification Report")
    plt.show()

# Example Usage
if __name__ == "__main__":
    import pandas as pd  # For creating the classification report heatmap

    # Example data
    input_movie = "Iron Man"
    system_recommendations = ["Iron Man 2", "Iron Man 3", "Edge of Tomorrow", "The Avengers", "Captain America: The Winter Soldier", "Guardians of the Galaxy"]  # Recommended by the system
    ground_truth = ["Iron Man 2", "Iron Man 3", "John Carter", "Avengers: Age of Ultron ", "The Avengers", "Captain America: The Winter Soldier"]  # Actual relevant movies

    # Evaluate the recommendation system
    evaluate_recommendation_system(input_movie, system_recommendations, ground_truth)
