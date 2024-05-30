# config.py
from ml_backtest.strategies import InvertedHammer, Hammer, BullishEngulfing, BullishHarami, DragonFlyDoji, MorningStar, PiercingPattern, MorningStarDoji # type: ignore
from ml_backtest.models import RandomForestRegressorTrainer # type: ignore

# Strategy Type Mapping
strategy_mappings = {
    'inverted-hammer': InvertedHammer,
    'hammer': Hammer,
    'bullish-engulfing': BullishEngulfing,
    'bullish-harami': BullishHarami,
    'dragonfly-doji': DragonFlyDoji,
    'morning-star': MorningStar,
    'piercing-pattern': PiercingPattern,
    'morning-star-doji': MorningStarDoji
}

# ML Type Mapping
ml_mappings = {
    'rfr': RandomForestRegressorTrainer,
}

def get_selection_strats():
    return [
        {'value': 'inverted-hammer', 'label': 'Inverted Hammer'},
        {'value': 'hammer', 'label': 'Hammer'},
        {'value': 'bullish-engulfing', 'label': 'Bullish Engulfing'},
        {'value': 'bullish-harami', 'label': 'Bullish Harami'},
        {'value': 'dragonfly-doji', 'label': 'Dragonfly Doji'},
        {'value': 'morning-star', 'label': 'Morning Star'},
        {'value': 'piercing-pattern', 'label': 'Piercing Pattern'},
        {'value': 'morning-star-doji', 'label': 'Morning Star Doji'},
    ]

def get_selection_models():
    return [
        {'value': 'rfr', 'label': 'Random Forest Regression'}
    ]

def get_column_names():
    return [
        {'id': 'SMA_Diff', 'label': 'SMA Diff'},
        {'id': 'EMA_Diff', 'label': 'EMA Diff'},
    ]
