import tkinter as tk
from tkinter import ttk

import darkdetect


class ThemeService:
    # Couleurs pour le mode clair
    LIGHT_THEME = {
        'bg': '#ffffff',
        'fg': '#000000',
        'button_bg': '#f0f0f0',
        'button_fg': '#000000',
        'entry_bg': '#ffffff',
        'entry_fg': '#000000',
        'tree_bg': '#ffffff',
        'tree_fg': '#000000',
        'selected_bg': '#0078d7',
        'selected_fg': '#ffffff',
        'card_bg': '#f8f8f8',
    }

    # Couleurs pour le mode sombre
    DARK_THEME = {
        'bg': '#2d2d2d',
        'fg': '#ffffff',
        'button_bg': '#3d3d3d',
        'button_fg': '#ffffff',
        'entry_bg': '#3d3d3d',
        'entry_fg': '#ffffff',
        'tree_bg': '#2d2d2d',
        'tree_fg': '#ffffff',
        'selected_bg': '#0078d7',
        'selected_fg': '#ffffff',
        'card_bg': '#3d3d3d',
    }

    @staticmethod
    def get_system_theme():
        """Détecte le thème système"""
        try:
            return 'dark' if darkdetect.isDark() else 'light'
        except:
            return 'light'  # Fallback en cas d'erreur

    @staticmethod
    def apply_theme(window):
        """Applique le thème approprié à la fenêtre"""
        theme = ThemeService.get_system_theme()
        colors = ThemeService.DARK_THEME if theme == 'dark' else ThemeService.LIGHT_THEME

        # Configuration du style
        style = ttk.Style(window)

        # Configuration générale
        window.configure(bg=colors['bg'])
        style.configure('.',
                        background=colors['bg'],
                        foreground=colors['fg']
                        )

        # Styles pour les widgets ttk
        style.configure('TFrame', background=colors['bg'])
        style.configure('TLabel',
                        background=colors['bg'],
                        foreground=colors['fg']
                        )
        style.configure('TButton',
                        background=colors['button_bg'],
                        foreground=colors['button_fg']
                        )
        style.configure('Action.TButton',
                        background=colors['button_bg'],
                        foreground=colors['button_fg']
                        )
        style.configure('TEntry',
                        fieldbackground=colors['entry_bg'],
                        foreground=colors['entry_fg']
                        )
        style.configure('Treeview',
                        background=colors['tree_bg'],
                        foreground=colors['tree_fg'],
                        fieldbackground=colors['tree_bg']
                        )
        style.configure('Treeview.Heading',
                        background=colors['button_bg'],
                        foreground=colors['button_fg']
                        )

        # Configuration des sélections
        style.map('Treeview',
                  background=[('selected', colors['selected_bg'])],
                  foreground=[('selected', colors['selected_fg'])]
                  )

        # Mise à jour des widgets existants
        for widget in window.winfo_children():
            ThemeService._update_widget_colors(widget, colors)

    @staticmethod
    def _update_widget_colors(widget, colors):
        """Met à jour récursivement les couleurs des widgets"""
        try:
            if isinstance(widget, (tk.Text, tk.Entry)):
                widget.configure(
                    bg=colors['entry_bg'],
                    fg=colors['entry_fg'],
                    insertbackground=colors['fg']
                )
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=colors['bg'])
            elif isinstance(widget, tk.Label):
                widget.configure(
                    bg=colors['bg'],
                    fg=colors['fg']
                )
            elif isinstance(widget, ttk.Frame):
                widget.configure(style='TFrame')
        except:
            pass  # Ignorer les widgets qui ne supportent pas certaines options

        # Récursion sur les widgets enfants
        for child in widget.winfo_children():
            ThemeService._update_widget_colors(child, colors)
