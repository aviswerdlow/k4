#!/usr/bin/env python3
"""
Token dictionary for Plan P: Codebook/Token segmentation
Survey/bearing/coordinate tokens for K4 analysis
"""

# Core token categories for surveying/navigation context
TOKENS = {
    # Compass directions (8 cardinal + 8 intercardinal)
    'COMPASS_CARDINAL': [
        'N', 'E', 'S', 'W',  # Primary
        'NE', 'NW', 'SE', 'SW',  # Secondary
    ],
    
    'COMPASS_FINE': [
        'NNE', 'ENE', 'ESE', 'SSE',  # Fine-grained
        'SSW', 'WSW', 'WNW', 'NNW'
    ],
    
    # Survey terms
    'SURVEY_UNITS': [
        'DEG', 'DEGREE', 'MIN', 'MINUTE', 'SEC', 'SECOND',
        'ROD', 'CHAIN', 'LINK', 'FOOT', 'FEET', 'FT',
        'YARD', 'YD', 'METER', 'M', 'KM', 'MILE', 'MI'
    ],
    
    'SURVEY_ACTIONS': [
        'GO', 'SET', 'READ', 'ALIGN', 'TURN', 'WALK',
        'PACE', 'MEASURE', 'MARK', 'FIND', 'DIG',
        'LOCATE', 'SURVEY', 'SIGHT', 'LEVEL'
    ],
    
    'SURVEY_FEATURES': [
        'POINT', 'PT', 'CORNER', 'STAKE', 'PIN', 'MARKER',
        'BENCH', 'BENCHMARK', 'BM', 'DATUM', 'REFERENCE',
        'LINE', 'BOUNDARY', 'EDGE', 'TREE', 'ROCK'
    ],
    
    # Bearing/Azimuth
    'BEARING_TERMS': [
        'BEARING', 'BEAR', 'AZ', 'AZIMUTH', 'TRUE', 'MAG',
        'MAGNETIC', 'GRID', 'COMPASS', 'HEADING', 'COURSE'
    ],
    
    # Numbers and modifiers
    'NUMBERS': [
        'ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE',
        'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN',
        'ELEVEN', 'TWELVE', 'THIRTEEN', 'FOURTEEN', 'FIFTEEN',
        'SIXTEEN', 'SEVENTEEN', 'EIGHTEEN', 'NINETEEN', 'TWENTY',
        'THIRTY', 'FORTY', 'FIFTY', 'SIXTY', 'SEVENTY',
        'EIGHTY', 'NINETY', 'HUNDRED', 'THOUSAND'
    ],
    
    'MODIFIERS': [
        'TO', 'FROM', 'AT', 'BY', 'OF', 'THE', 'A', 'AN',
        'AND', 'OR', 'THEN', 'NEXT', 'FIRST', 'LAST',
        'LEFT', 'RIGHT', 'UP', 'DOWN', 'FORWARD', 'BACK'
    ],
    
    # Time references (relevant to CLOCK anchor)
    'TIME_TERMS': [
        'HOUR', 'HR', 'MINUTE', 'MIN', 'SECOND', 'SEC',
        'CLOCK', 'TIME', 'WATCH', 'NOON', 'MIDNIGHT',
        'AM', 'PM', 'ZONE', 'GMT', 'UTC', 'LOCAL'
    ],
    
    # Geographic/location
    'LOCATION_TERMS': [
        'EAST', 'NORTHEAST', 'BERLIN', 'CLOCK',  # Our anchors
        'CITY', 'TOWN', 'SITE', 'PLACE', 'LOCATION',
        'COORDINATE', 'COORD', 'LAT', 'LATITUDE', 'LON',
        'LONGITUDE', 'POSITION', 'POS', 'GPS'
    ],
    
    # Crypto/Kryptos specific
    'KRYPTOS_TERMS': [
        'KRYPTOS', 'SANBORN', 'CIA', 'LANGLEY', 'SCULPTURE',
        'PANEL', 'SECTION', 'CODE', 'CIPHER', 'KEY',
        'VIGENERE', 'TRANSPOSITION', 'TABLEAU', 'ALPHABET'
    ]
}

def get_all_tokens():
    """Get flat list of all tokens"""
    all_tokens = []
    for category in TOKENS.values():
        all_tokens.extend(category)
    return all_tokens

def get_token_lengths():
    """Get tokens grouped by length"""
    tokens_by_length = {}
    for token in get_all_tokens():
        length = len(token)
        if length not in tokens_by_length:
            tokens_by_length[length] = []
        tokens_by_length[length].append(token)
    return tokens_by_length

def is_token(word):
    """Check if a word is a valid token"""
    all_tokens = get_all_tokens()
    return word.upper() in all_tokens

def get_token_category(word):
    """Get the category of a token"""
    word_upper = word.upper()
    for category, tokens in TOKENS.items():
        if word_upper in tokens:
            return category
    return None

# Create lookup structures for efficient segmentation
TOKEN_SET = set(get_all_tokens())
MAX_TOKEN_LENGTH = max(len(token) for token in TOKEN_SET)
MIN_TOKEN_LENGTH = min(len(token) for token in TOKEN_SET)

# Token scoring weights (prefer longer, more specific tokens)
TOKEN_SCORES = {}
for token in TOKEN_SET:
    base_score = len(token)  # Longer tokens score higher
    
    # Bonus for specific categories
    category = get_token_category(token)
    if category in ['SURVEY_ACTIONS', 'BEARING_TERMS', 'SURVEY_FEATURES']:
        base_score *= 1.5
    elif category in ['COMPASS_CARDINAL', 'COMPASS_FINE']:
        base_score *= 1.3
    elif category == 'LOCATION_TERMS':
        base_score *= 1.2
    
    TOKEN_SCORES[token] = base_score

if __name__ == "__main__":
    print(f"Token dictionary loaded: {len(TOKEN_SET)} tokens")
    print(f"Token length range: {MIN_TOKEN_LENGTH}-{MAX_TOKEN_LENGTH}")
    
    # Show sample tokens by category
    for category, tokens in TOKENS.items():
        print(f"\n{category}: {tokens[:5]}...")