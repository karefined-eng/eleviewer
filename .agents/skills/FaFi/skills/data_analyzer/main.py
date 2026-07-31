"""
Data Analyzer Skill
===================
Analysiert strukturierte Daten und erstellt Statistiken.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union


def execute(data: Union[str, List[Dict], Dict], 
            analysis_type: str = "summary",
            columns: List[str] = None) -> Dict[str, Any]:
    """
    Analysiert Daten und erstellt statistische Zusammenfassungen.
    
    Args:
        data: Daten als Liste von Dicts, Dict, oder Pfad zu CSV
        analysis_type: Art der Analyse (summary, correlation, distribution, trends)
        columns: Spezifische Spalten für die Analyse
        
    Returns:
        Dictionary mit analysis, insights, statistics
    """
    # Lade Daten in DataFrame
    df = _load_data(data)
    
    if df is None or df.empty:
        return {
            'analysis': {'error': 'Keine Daten zum Analysieren'},
            'insights': [],
            'statistics': {}
        }
    
    # Filtere Spalten falls angegeben
    if columns:
        available_cols = [c for c in columns if c in df.columns]
        if available_cols:
            df = df[available_cols]
    
    # Führe Analyse durch
    if analysis_type == 'summary':
        analysis = _summary_analysis(df)
    elif analysis_type == 'correlation':
        analysis = _correlation_analysis(df)
    elif analysis_type == 'distribution':
        analysis = _distribution_analysis(df)
    elif analysis_type == 'trends':
        analysis = _trend_analysis(df)
    else:
        analysis = _summary_analysis(df)
    
    # Generiere Erkenntnisse
    insights = _generate_insights(df, analysis_type)
    
    # Berechne Statistiken
    statistics = _calculate_statistics(df)
    
    return {
        'analysis': analysis,
        'insights': insights,
        'statistics': statistics
    }


def _load_data(data: Union[str, List[Dict], Dict]) -> pd.DataFrame:
    """Lädt Daten in einen DataFrame."""
    try:
        if isinstance(data, str):
            # Pfad zu CSV
            return pd.read_csv(data)
        elif isinstance(data, list):
            # Liste von Dictionaries
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            # Dictionary mit Listen
            return pd.DataFrame(data)
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Fehler beim Laden: {e}")
        return pd.DataFrame()


def _summary_analysis(df: pd.DataFrame) -> Dict:
    """Erstellt eine Zusammenfassungsanalyse."""
    summary = {
        'row_count': len(df),
        'column_count': len(df.columns),
        'columns': list(df.columns),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_summary': {}
    }
    
    # Numerische Spalten zusammenfassen
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        summary['numeric_summary'][col] = {
            'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
            'median': float(df[col].median()) if not pd.isna(df[col].median()) else None,
            'std': float(df[col].std()) if not pd.isna(df[col].std()) else None,
            'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
            'max': float(df[col].max()) if not pd.isna(df[col].max()) else None
        }
    
    return summary


def _correlation_analysis(df: pd.DataFrame) -> Dict:
    """Berechnet Korrelationen zwischen numerischen Spalten."""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty or len(numeric_df.columns) < 2:
        return {'error': 'Mindestens 2 numerische Spalten benötigt'}
    
    corr_matrix = numeric_df.corr()
    
    # Finde starke Korrelationen
    strong_correlations = []
    for i, col1 in enumerate(corr_matrix.columns):
        for j, col2 in enumerate(corr_matrix.columns):
            if i < j:
                corr_value = corr_matrix.loc[col1, col2]
                if abs(corr_value) > 0.5:
                    strong_correlations.append({
                        'column1': col1,
                        'column2': col2,
                        'correlation': round(corr_value, 3),
                        'strength': 'stark' if abs(corr_value) > 0.7 else 'moderat'
                    })
    
    return {
        'correlation_matrix': corr_matrix.to_dict(),
        'strong_correlations': strong_correlations
    }


def _distribution_analysis(df: pd.DataFrame) -> Dict:
    """Analysiert die Verteilung der Daten."""
    distributions = {}
    
    for col in df.columns:
        if df[col].dtype in [np.int64, np.float64]:
            # Numerische Verteilung
            distributions[col] = {
                'type': 'numeric',
                'quartiles': {
                    'q1': float(df[col].quantile(0.25)),
                    'q2': float(df[col].quantile(0.50)),
                    'q3': float(df[col].quantile(0.75))
                },
                'skewness': float(df[col].skew()) if len(df[col].dropna()) > 2 else None,
                'kurtosis': float(df[col].kurtosis()) if len(df[col].dropna()) > 3 else None
            }
        else:
            # Kategorische Verteilung
            value_counts = df[col].value_counts().head(10)
            distributions[col] = {
                'type': 'categorical',
                'unique_values': int(df[col].nunique()),
                'top_values': value_counts.to_dict()
            }
    
    return distributions


def _trend_analysis(df: pd.DataFrame) -> Dict:
    """Analysiert Trends in den Daten."""
    trends = {}
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        values = df[col].dropna().values
        if len(values) < 3:
            continue
        
        # Einfache Trendberechnung
        x = np.arange(len(values))
        try:
            slope, intercept = np.polyfit(x, values, 1)
            trends[col] = {
                'slope': round(slope, 4),
                'direction': 'steigend' if slope > 0 else 'fallend' if slope < 0 else 'stabil',
                'change_percent': round((values[-1] - values[0]) / values[0] * 100, 2) if values[0] != 0 else None
            }
        except:
            pass
    
    return trends


def _generate_insights(df: pd.DataFrame, analysis_type: str) -> List[str]:
    """Generiert automatische Erkenntnisse."""
    insights = []
    
    # Allgemeine Erkenntnisse
    insights.append(f"Der Datensatz enthält {len(df)} Zeilen und {len(df.columns)} Spalten.")
    
    # Fehlende Werte
    missing = df.isnull().sum()
    cols_with_missing = missing[missing > 0]
    if len(cols_with_missing) > 0:
        insights.append(f"{len(cols_with_missing)} Spalte(n) enthalten fehlende Werte.")
    
    # Numerische Erkenntnisse
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols[:3]:  # Limitiere auf 3 Spalten
        mean_val = df[col].mean()
        std_val = df[col].std()
        if std_val and mean_val:
            cv = std_val / abs(mean_val) * 100
            if cv > 50:
                insights.append(f"'{col}' zeigt hohe Variabilität (CV: {cv:.1f}%).")
    
    return insights


def _calculate_statistics(df: pd.DataFrame) -> Dict:
    """Berechnet grundlegende Statistiken."""
    stats = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
        'categorical_columns': len(df.select_dtypes(include=['object', 'category']).columns),
        'completeness': round((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100, 2)
    }
    
    return stats


# Für direkten Aufruf
if __name__ == "__main__":
    import sys
    import json
    
    # Beispieldaten
    sample_data = [
        {'name': 'A', 'value': 10, 'category': 'X'},
        {'name': 'B', 'value': 20, 'category': 'Y'},
        {'name': 'C', 'value': 15, 'category': 'X'},
        {'name': 'D', 'value': 25, 'category': 'Y'},
    ]
    
    result = execute(sample_data, 'summary')
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
