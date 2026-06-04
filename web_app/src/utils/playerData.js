export const getCountryInfo = (teamName) => {
  const map = {
    'Spain': { code: 'es', playerId: 201153 },
    'Serbia': { code: 'rs', playerId: 199434 },
    'Argentina': { code: 'ar', playerId: 158023 },
    'Peru': { code: 'pe', playerId: 207669 },
    'France': { code: 'fr', playerId: 231747 },
    'Egypt': { code: 'eg', playerId: 209331 },
    'England': { code: 'gb-eng', playerId: 202126 },
    'United States': { code: 'us', playerId: 227796 },
    'Brazil': { code: 'br', playerId: 200145 },
    'Scotland': { code: 'gb-sct', playerId: 216267 },
    'Portugal': { code: 'pt', playerId: 20801 },
    'Australia': { code: 'au', playerId: 199005 },
    'Netherlands': { code: 'nl', playerId: 203376 },
    'South Korea': { code: 'kr', playerId: 200104 },
    'Germany': { code: 'de', playerId: 212622 },
    'Paraguay': { code: 'py', playerId: 230142 },
    'Colombia': { code: 'co', playerId: 231410 },
    'Iran': { code: 'ir', playerId: 214997 },
    'Croatia': { code: 'hr', playerId: 177003 },
    'Canada': { code: 'ca', playerId: 234396 },
    'Morocco': { code: 'ma', playerId: 235212 },
    'Nigeria': { code: 'ng', playerId: 232293 },
    'Italy': { code: 'it', playerId: 230621 },
    'Senegal': { code: 'sn', playerId: 201024 },
    'Japan': { code: 'jp', playerId: 237681 },
    'Turkey': { code: 'tr', playerId: 215333 },
    'Ecuador': { code: 'ec', playerId: 259608 },
    'Denmark': { code: 'dk', playerId: 210514 },
    'Uruguay': { code: 'uy', playerId: 239053 },
    'Switzerland': { code: 'ch', playerId: 199503 },
    'Belgium': { code: 'be', playerId: 192985 },
    'Mexico': { code: 'mx', playerId: 235844 },
    'New Zealand': { code: 'nz', playerId: null },
    'Trinidad and Tobago': { code: 'tt', playerId: null },
    'Uzbekistan': { code: 'uz', playerId: null },
    'Jamaica': { code: 'jm', playerId: null },
    'Bolivia': { code: 'bo', playerId: null },
    'Bahrain': { code: 'bh', playerId: null },
    'Panama': { code: 'pa', playerId: null },
    'Albania': { code: 'al', playerId: null },
    'Saudi Arabia': { code: 'sa', playerId: null },
    'Indonesia': { code: 'id', playerId: null },
    'Cameroon': { code: 'cm', playerId: null },
    'Honduras': { code: 'hn', playerId: null },
    'Ivory Coast': { code: 'ci', playerId: null },
    'Tunisia': { code: 'tn', playerId: null },
    'Qatar': { code: 'qa', playerId: null },
    'Poland': { code: 'pl', playerId: null }
  };
  return map[teamName] || { code: null, playerId: null };
};

export const getStarPlayer = (team) => {
  const stars = {
    'Spain': 'Lamine Yamal',
    'Argentina': 'Lionel Messi',
    'France': 'Kylian Mbappé',
    'England': 'Jude Bellingham',
    'Brazil': 'Vinícius Júnior',
    'Portugal': 'Cristiano Ronaldo',
    'Netherlands': 'Virgil van Dijk',
    'Germany': 'Thomas Müller',
    'Colombia': 'Luis Díaz',
    'Croatia': 'Luka Modrić'
  };
  return stars[team] || 'Top Goalscorer';
};
