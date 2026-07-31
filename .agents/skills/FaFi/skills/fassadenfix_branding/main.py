"""
FassadenFix Branding Skill
==========================
Wendet FassadenFix Corporate Design und Branding-Richtlinien automatisch an.

STANDARD-SKILL: Ist bei allen Anwendungen, Modulen, Agents und Plattformen 
standardmäßig aktiviert (Opt-Out-Prinzip/Widerspruchslösung).
"""

from typing import Dict, Any, List, Optional
import json

# ============================================================================
# FASSADENFIX BRAND CONSTANTS
# ============================================================================

COLORS = {
    # Primärfarben
    "primary": "#77bc1f",
    "primary_dark": "#6aa91b",
    "primary_light": "#8fcc3f",
    
    # Sekundärfarben
    "secondary": "#4e5758",
    "secondary_light": "#6b7577",
    
    # Neutrale Farben
    "white": "#ffffff",
    "black": "#000000",
    "gray_50": "#f9fafb",
    "gray_100": "#f3f4f6",
    "gray_200": "#e5e7eb",
    "gray_300": "#d1d5db",
    "gray_600": "#4b5563",
    "gray_900": "#111827",
    
    # Aliase für Kompatibilität
    "ff_green": "#77bc1f",
    "ff_gray": "#4e5758",
}

TYPOGRAPHY = {
    "font_family": "'Raleway', sans-serif",
    "font_import": "https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600;700;800&display=swap",
    "weights": {
        "regular": 400,
        "medium": 500,
        "semibold": 600,
        "bold": 700,
        "extrabold": 800,
    },
    "sizes": {
        "xs": "0.75rem",
        "sm": "0.875rem",
        "base": "1rem",
        "lg": "1.125rem",
        "xl": "1.25rem",
        "2xl": "1.5rem",
        "3xl": "1.875rem",
        "4xl": "2.25rem",
        "5xl": "3rem",
    },
    "line_height": 1.6,
}

SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "2xl": "48px",
    "3xl": "64px",
}

BORDER_RADIUS = {
    "sm": "4px",
    "md": "8px",
    "lg": "12px",
    "xl": "16px",
    "full": "9999px",
}

SHADOWS = {
    "sm": "0 1px 2px rgba(78, 87, 88, 0.1)",
    "md": "0 4px 6px rgba(78, 87, 88, 0.1)",
    "lg": "0 10px 15px rgba(78, 87, 88, 0.1)",
    "xl": "0 20px 25px rgba(78, 87, 88, 0.15)",
}

TRANSITIONS = {
    "fast": "150ms ease",
    "base": "300ms ease",
    "slow": "500ms ease",
}

# Opt-Out Keywords für die Erkennung
OPT_OUT_KEYWORDS = [
    "--no-branding",
    "--skip-fassadenfix-style",
    "branding: false",
    "ohne fassadenfix branding",
    "abweichendes design",
    "custom branding",
    "eigenes design",
    "no branding",
    "skip branding",
]


def check_opt_out(context: str = "") -> bool:
    """
    Prüft, ob ein Opt-Out für das Branding angefordert wurde.
    
    Args:
        context: Kontext-String, der auf Opt-Out-Keywords geprüft wird
        
    Returns:
        True wenn Opt-Out erkannt wurde, sonst False
    """
    if not context:
        return False
    
    context_lower = context.lower()
    return any(keyword.lower() in context_lower for keyword in OPT_OUT_KEYWORDS)


def generate_css_variables() -> str:
    """Generiert CSS Custom Properties für das FassadenFix Branding."""
    
    css = f""":root {{
  /* === FASSADENFIX BRANDING === */
  
  /* Primärfarben */
  --ff-green: {COLORS['primary']};
  --ff-green-dark: {COLORS['primary_dark']};
  --ff-green-light: {COLORS['primary_light']};
  --color-primary: var(--ff-green);
  --color-primary-dark: var(--ff-green-dark);
  --color-primary-light: var(--ff-green-light);
  
  /* Sekundärfarben */
  --ff-gray: {COLORS['secondary']};
  --ff-gray-light: {COLORS['secondary_light']};
  --color-secondary: var(--ff-gray);
  --color-secondary-light: var(--ff-gray-light);
  
  /* Neutrale Farben */
  --color-white: {COLORS['white']};
  --color-black: {COLORS['black']};
  --color-gray-50: {COLORS['gray_50']};
  --color-gray-100: {COLORS['gray_100']};
  --color-gray-200: {COLORS['gray_200']};
  --color-gray-300: {COLORS['gray_300']};
  --color-gray-600: {COLORS['gray_600']};
  --color-gray-900: {COLORS['gray_900']};
  
  /* Typografie */
  --font-family: {TYPOGRAPHY['font_family']};
  --font-weight-regular: {TYPOGRAPHY['weights']['regular']};
  --font-weight-medium: {TYPOGRAPHY['weights']['medium']};
  --font-weight-semibold: {TYPOGRAPHY['weights']['semibold']};
  --font-weight-bold: {TYPOGRAPHY['weights']['bold']};
  --font-weight-extrabold: {TYPOGRAPHY['weights']['extrabold']};
  
  /* Font Sizes */
  --text-xs: {TYPOGRAPHY['sizes']['xs']};
  --text-sm: {TYPOGRAPHY['sizes']['sm']};
  --text-base: {TYPOGRAPHY['sizes']['base']};
  --text-lg: {TYPOGRAPHY['sizes']['lg']};
  --text-xl: {TYPOGRAPHY['sizes']['xl']};
  --text-2xl: {TYPOGRAPHY['sizes']['2xl']};
  --text-3xl: {TYPOGRAPHY['sizes']['3xl']};
  --text-4xl: {TYPOGRAPHY['sizes']['4xl']};
  --text-5xl: {TYPOGRAPHY['sizes']['5xl']};
  
  /* Spacing */
  --spacing-xs: {SPACING['xs']};
  --spacing-sm: {SPACING['sm']};
  --spacing-md: {SPACING['md']};
  --spacing-lg: {SPACING['lg']};
  --spacing-xl: {SPACING['xl']};
  --spacing-2xl: {SPACING['2xl']};
  --spacing-3xl: {SPACING['3xl']};
  
  /* Border Radius */
  --radius-sm: {BORDER_RADIUS['sm']};
  --radius-md: {BORDER_RADIUS['md']};
  --radius-lg: {BORDER_RADIUS['lg']};
  --radius-xl: {BORDER_RADIUS['xl']};
  --radius-full: {BORDER_RADIUS['full']};
  
  /* Shadows */
  --shadow-sm: {SHADOWS['sm']};
  --shadow-md: {SHADOWS['md']};
  --shadow-lg: {SHADOWS['lg']};
  --shadow-xl: {SHADOWS['xl']};
  
  /* Transitions */
  --transition-fast: {TRANSITIONS['fast']};
  --transition-base: {TRANSITIONS['base']};
  --transition-slow: {TRANSITIONS['slow']};
  
  /* Gradients */
  --gradient-primary: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%);
  --gradient-hero: linear-gradient(135deg, {COLORS['secondary']} 0%, {COLORS['primary']} 100%);
}}
"""
    
    return css


def generate_base_styles() -> str:
    """Generiert Basis-CSS-Styles für das FassadenFix Branding."""
    
    return """/* FassadenFix Base Styles */

body {
  font-family: var(--font-family);
  font-weight: var(--font-weight-regular);
  color: var(--color-secondary);
  line-height: 1.6;
  background-color: var(--color-white);
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-family);
  font-weight: var(--font-weight-bold);
  color: var(--color-secondary);
  margin-bottom: var(--spacing-md);
}

h1 { font-size: var(--text-5xl); }
h2 { font-size: var(--text-4xl); }
h3 { font-size: var(--text-3xl); }
h4 { font-size: var(--text-2xl); }
h5 { font-size: var(--text-xl); }
h6 { font-size: var(--text-lg); }

a {
  color: var(--color-primary);
  text-decoration: none;
  transition: var(--transition-base);
}

a:hover {
  color: var(--color-primary-dark);
}

/* Primary Button */
.btn-primary {
  background-color: var(--color-primary);
  color: var(--color-white);
  font-family: var(--font-family);
  font-weight: var(--font-weight-bold);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-lg);
  border: none;
  cursor: pointer;
  transition: var(--transition-base);
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
  box-shadow: 0 4px 6px rgba(119, 188, 31, 0.3);
}

/* Secondary Button */
.btn-secondary {
  background-color: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
  font-family: var(--font-family);
  font-weight: var(--font-weight-semibold);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-lg);
  cursor: pointer;
  transition: var(--transition-base);
}

.btn-secondary:hover {
  background-color: var(--color-primary);
  color: var(--color-white);
}

/* Card */
.card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: var(--spacing-lg);
}

/* Navigation */
.nav {
  background: var(--color-white);
  box-shadow: var(--shadow-sm);
}

.nav-link {
  color: var(--color-secondary);
  font-weight: var(--font-weight-medium);
  transition: var(--transition-base);
}

.nav-link:hover,
.nav-link.active {
  color: var(--color-primary);
}

/* Footer */
.footer {
  background: var(--color-secondary);
  color: var(--color-white);
  padding: var(--spacing-2xl) var(--spacing-lg);
}

.footer a {
  color: var(--color-white);
}

.footer a:hover {
  color: var(--color-primary);
}

/* Input Fields */
input, textarea, select {
  font-family: var(--font-family);
  border: 1px solid var(--color-gray-300);
  border-radius: var(--radius-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  transition: var(--transition-base);
}

input:focus, textarea:focus, select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(119, 188, 31, 0.2);
}
"""


def generate_tailwind_config() -> str:
    """Generiert Tailwind CSS Konfiguration für das FassadenFix Branding."""
    
    config = {
        "theme": {
            "extend": {
                "colors": {
                    "ff-green": COLORS["primary"],
                    "ff-gray": COLORS["secondary"],
                    "primary": {
                        "DEFAULT": COLORS["primary"],
                        "dark": COLORS["primary_dark"],
                        "light": COLORS["primary_light"],
                    },
                    "secondary": {
                        "DEFAULT": COLORS["secondary"],
                        "light": COLORS["secondary_light"],
                    },
                },
                "fontFamily": {
                    "sans": ["Raleway", "sans-serif"],
                },
                "fontWeight": {
                    "normal": "400",
                    "medium": "500",
                    "semibold": "600",
                    "bold": "700",
                    "extrabold": "800",
                },
                "borderRadius": BORDER_RADIUS,
                "boxShadow": SHADOWS,
            },
        },
    }
    
    return f"// tailwind.config.js\nmodule.exports = {json.dumps(config, indent=2)}"


def generate_scss_variables() -> str:
    """Generiert SCSS Variablen für das FassadenFix Branding."""
    
    scss = f"""// FassadenFix SCSS Variables

// Primärfarben
$ff-green: {COLORS['primary']};
$ff-green-dark: {COLORS['primary_dark']};
$ff-green-light: {COLORS['primary_light']};

// Sekundärfarben
$ff-gray: {COLORS['secondary']};
$ff-gray-light: {COLORS['secondary_light']};

// Neutrale Farben
$white: {COLORS['white']};
$black: {COLORS['black']};
$gray-50: {COLORS['gray_50']};
$gray-100: {COLORS['gray_100']};
$gray-200: {COLORS['gray_200']};
$gray-300: {COLORS['gray_300']};
$gray-600: {COLORS['gray_600']};
$gray-900: {COLORS['gray_900']};

// Typografie
$font-family: {TYPOGRAPHY['font_family']};
$font-weight-regular: {TYPOGRAPHY['weights']['regular']};
$font-weight-medium: {TYPOGRAPHY['weights']['medium']};
$font-weight-semibold: {TYPOGRAPHY['weights']['semibold']};
$font-weight-bold: {TYPOGRAPHY['weights']['bold']};
$font-weight-extrabold: {TYPOGRAPHY['weights']['extrabold']};

// Font Sizes
$text-xs: {TYPOGRAPHY['sizes']['xs']};
$text-sm: {TYPOGRAPHY['sizes']['sm']};
$text-base: {TYPOGRAPHY['sizes']['base']};
$text-lg: {TYPOGRAPHY['sizes']['lg']};
$text-xl: {TYPOGRAPHY['sizes']['xl']};
$text-2xl: {TYPOGRAPHY['sizes']['2xl']};
$text-3xl: {TYPOGRAPHY['sizes']['3xl']};
$text-4xl: {TYPOGRAPHY['sizes']['4xl']};
$text-5xl: {TYPOGRAPHY['sizes']['5xl']};

// Spacing
$spacing-xs: {SPACING['xs']};
$spacing-sm: {SPACING['sm']};
$spacing-md: {SPACING['md']};
$spacing-lg: {SPACING['lg']};
$spacing-xl: {SPACING['xl']};
$spacing-2xl: {SPACING['2xl']};
$spacing-3xl: {SPACING['3xl']};

// Border Radius
$radius-sm: {BORDER_RADIUS['sm']};
$radius-md: {BORDER_RADIUS['md']};
$radius-lg: {BORDER_RADIUS['lg']};
$radius-xl: {BORDER_RADIUS['xl']};
$radius-full: {BORDER_RADIUS['full']};

// Shadows
$shadow-sm: {SHADOWS['sm']};
$shadow-md: {SHADOWS['md']};
$shadow-lg: {SHADOWS['lg']};
$shadow-xl: {SHADOWS['xl']};

// Transitions
$transition-fast: {TRANSITIONS['fast']};
$transition-base: {TRANSITIONS['base']};
$transition-slow: {TRANSITIONS['slow']};
"""
    
    return scss


def execute(
    apply_branding: bool = True,
    output_format: str = "css",
    components: List[str] = None,
    context: str = ""
) -> Dict[str, Any]:
    """
    Hauptfunktion des FassadenFix Branding Skills.
    
    Args:
        apply_branding: Branding anwenden (Standard: True). Auf False setzen für Opt-Out.
        output_format: Ausgabeformat ('css', 'tailwind', 'json', 'scss')
        components: Spezifische Komponenten zum Stylen (leer = alle)
        context: Kontext-String für Opt-Out-Erkennung
        
    Returns:
        Dictionary mit Styles, Farben, Typografie und Branding-Status
    """
    
    # Prüfe auf Opt-Out
    if not apply_branding or check_opt_out(context):
        return {
            "styles": "",
            "colors": {},
            "typography": {},
            "branding_applied": False,
            "message": "FassadenFix Branding wurde deaktiviert (Opt-Out)"
        }
    
    # Generiere Styles basierend auf Format
    if output_format == "css":
        styles = generate_css_variables() + "\n\n" + generate_base_styles()
    elif output_format == "tailwind":
        styles = generate_tailwind_config()
    elif output_format == "scss":
        styles = generate_scss_variables()
    elif output_format == "json":
        styles = json.dumps({
            "colors": COLORS,
            "typography": TYPOGRAPHY,
            "spacing": SPACING,
            "borderRadius": BORDER_RADIUS,
            "shadows": SHADOWS,
            "transitions": TRANSITIONS,
        }, indent=2)
    else:
        styles = generate_css_variables()
    
    return {
        "styles": styles,
        "colors": COLORS,
        "typography": TYPOGRAPHY,
        "spacing": SPACING,
        "border_radius": BORDER_RADIUS,
        "shadows": SHADOWS,
        "transitions": TRANSITIONS,
        "branding_applied": True,
        "font_import": f'<link href="{TYPOGRAPHY["font_import"]}" rel="stylesheet">',
        "message": "FassadenFix Branding wurde erfolgreich angewendet"
    }


def get_color(name: str) -> str:
    """Gibt eine FassadenFix Farbe zurück."""
    return COLORS.get(name, COLORS["primary"])


def get_font_import() -> str:
    """Gibt den Google Fonts Import-Link zurück."""
    return f'<link href="{TYPOGRAPHY["font_import"]}" rel="stylesheet">'


def is_default_enabled() -> bool:
    """Gibt zurück, ob dieser Skill standardmäßig aktiviert ist."""
    return True


def get_priority() -> int:
    """Gibt die Priorität dieses Skills zurück (höher = wichtiger)."""
    return 100


def get_scope() -> str:
    """Gibt den Geltungsbereich dieses Skills zurück."""
    return "global"


# Für direkten Aufruf
if __name__ == "__main__":
    import sys
    
    output_format = sys.argv[1] if len(sys.argv) > 1 else "css"
    
    result = execute(output_format=output_format)
    
    print(f"FassadenFix Branding - Format: {output_format}")
    print("=" * 60)
    print(result["styles"])
    print("\n" + "=" * 60)
    print(f"Branding angewendet: {result['branding_applied']}")
