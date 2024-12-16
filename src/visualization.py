import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
from datetime import datetime, timedelta
import numpy as np
from typing import List, Dict


class ProgressVisualization:
    def __init__(self, stats: Dict):
        self.stats = stats

    def create_accuracy_over_time(self, frame: ttk.Frame) -> None:
        """Create accuracy over time line chart"""
        fig, ax = plt.subplots(figsize=(8, 4))

        # Collect data points
        dates = []
        accuracies = []

        for class_name, sessions in self.stats.items():
            for session in sessions:
                dates.append(datetime.fromisoformat(session['timestamp']))
                accuracies.append(session['accuracy'])

        # Sort by date
        if dates:
            sorted_points = sorted(zip(dates, accuracies))
            dates, accuracies = zip(*sorted_points)

            # Plot
            ax.plot(dates, accuracies, marker='o')
            ax.set_title('Accuracy Over Time')
            ax.set_xlabel('Study Date')
            ax.set_ylabel('Accuracy (%)')
            ax.grid(True)

            # Rotate date labels
            plt.xticks(rotation=45)

            # Add trend line
            z = np.polyfit(range(len(dates)), accuracies, 1)
            p = np.poly1d(z)
            ax.plot(dates, p(range(len(dates))), "r--", alpha=0.8)

            # Adjust layout
            plt.tight_layout()

            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)

    def create_class_performance(self, frame: ttk.Frame) -> None:
        """Create bar chart of performance by class"""
        fig, ax = plt.subplots(figsize=(8, 4))

        # Calculate average accuracy per class
        class_accuracies = {}
        for class_name, sessions in self.stats.items():
            accuracies = [s['accuracy'] for s in sessions]
            class_accuracies[class_name] = sum(accuracies) / len(accuracies)

        if class_accuracies:
            classes = list(class_accuracies.keys())
            accuracies = list(class_accuracies.values())

            # Create bar chart
            bars = ax.bar(classes, accuracies)
            ax.set_title('Average Performance by Class')
            ax.set_xlabel('Class')
            ax.set_ylabel('Average Accuracy (%)')

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height,
                        f'{height:.1f}%',
                        ha='center', va='bottom')

            # Rotate class labels if needed
            plt.xticks(rotation=45 if len(classes) > 5 else 0)

            # Adjust layout
            plt.tight_layout()

            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)

    def create_study_frequency(self, frame: ttk.Frame) -> None:
        """Create study frequency heatmap"""
        fig, ax = plt.subplots(figsize=(8, 4))

        # Count sessions per day
        session_counts = {}
        for class_name, sessions in self.stats.items():
            for session in sessions:
                date = datetime.fromisoformat(session['timestamp']).date()
                session_counts[date] = session_counts.get(date, 0) + 1

        if session_counts:
            dates = sorted(session_counts.keys())
            counts = [session_counts[date] for date in dates]

            # Create line plot
            ax.plot(dates, counts, marker='o')
            ax.set_title('Study Frequency')
            ax.set_xlabel('Date')
            ax.set_ylabel('Sessions')

            # Rotate date labels
            plt.xticks(rotation=45)

            # Adjust layout
            plt.tight_layout()

            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)

    def create_learning_curve(self, frame: ttk.Frame) -> None:
        """Create learning curve analysis chart"""
        fig, ax = plt.subplots(figsize=(8, 4))

        # Collect data for learning curve
        class_learning_data = {}

        for class_name, sessions in self.stats.items():
            # Sort sessions by date
            sorted_sessions = sorted(sessions, key=lambda x: datetime.fromisoformat(x['timestamp']))

            # Calculate cumulative moving average
            accuracies = [s['accuracy'] for s in sorted_sessions]
            cumulative_avg = []
            total = 0

            for i, acc in enumerate(accuracies, 1):
                total += acc
                cumulative_avg.append(total / i)

            class_learning_data[class_name] = {
                'sessions': range(1, len(accuracies) + 1),
                'cumulative_avg': cumulative_avg
            }

        if class_learning_data:
            # Plot learning curves for each class
            for class_name, data in class_learning_data.items():
                ax.plot(data['sessions'], data['cumulative_avg'],
                        marker='o', label=class_name, alpha=0.7)

                # Add trend line
                z = np.polyfit(data['sessions'], data['cumulative_avg'], 2)  # Quadratic fit
                p = np.poly1d(z)
                x_trend = np.linspace(min(data['sessions']), max(data['sessions']), 100)
                ax.plot(x_trend, p(x_trend), '--', alpha=0.5)

            ax.set_title('Learning Curve Analysis')
            ax.set_xlabel('Study Sessions')
            ax.set_ylabel('Cumulative Average Accuracy (%)')
            ax.grid(True, alpha=0.3)
            ax.legend()

            # Add mastery line at 90%
            ax.axhline(y=90, color='g', linestyle='--', alpha=0.3, label='Mastery Level')

            # Adjust layout
            plt.tight_layout()

            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)

    def create_retention_analysis(self, frame: ttk.Frame) -> None:
        """Create retention analysis chart"""
        fig, ax = plt.subplots(figsize=(8, 4))

        # Analyze retention between sessions
        retention_data = {}

        for class_name, sessions in self.stats.items():
            if len(sessions) < 2:
                continue

            # Sort sessions by date
            sorted_sessions = sorted(sessions, key=lambda x: datetime.fromisoformat(x['timestamp']))

            # Calculate retention (difference between consecutive sessions)
            retention_scores = []
            time_gaps = []

            for i in range(1, len(sorted_sessions)):
                prev_acc = sorted_sessions[i - 1]['accuracy']
                curr_acc = sorted_sessions[i]['accuracy']

                # Calculate time gap in days
                prev_time = datetime.fromisoformat(sorted_sessions[i - 1]['timestamp'])
                curr_time = datetime.fromisoformat(sorted_sessions[i]['timestamp'])
                gap_days = (curr_time - prev_time).days

                retention_scores.append(curr_acc - prev_acc)
                time_gaps.append(gap_days)

            retention_data[class_name] = {
                'gaps': time_gaps,
                'retention': retention_scores
            }

        if retention_data:
            # Plot retention analysis
            for class_name, data in retention_data.items():
                ax.scatter(data['gaps'], data['retention'],
                           label=class_name, alpha=0.7)

                # Add trend line
                if len(data['gaps']) > 1:
                    z = np.polyfit(data['gaps'], data['retention'], 1)
                    p = np.poly1d(z)
                    x_trend = np.linspace(min(data['gaps']), max(data['gaps']), 100)
                    ax.plot(x_trend, p(x_trend), '--', alpha=0.5)

            ax.set_title('Retention Analysis')
            ax.set_xlabel('Days Between Sessions')
            ax.set_ylabel('Accuracy Change (%)')
            ax.grid(True, alpha=0.3)
            ax.legend()

            # Add reference line at y=0
            ax.axhline(y=0, color='k', linestyle='-', alpha=0.2)

            # Adjust layout
            plt.tight_layout()

            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)
