const fs = require('fs');

const dataPath = './public/data.json';
const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

const enrichments = {
  "Spain": { fifa_rating: 85, squad_value_m: 850, home_continent: "Europe", star_player_count: 4 },
  "Argentina": { fifa_rating: 86, squad_value_m: 800, home_continent: "South America", star_player_count: 5 },
  "France": { fifa_rating: 87, squad_value_m: 1050, home_continent: "Europe", star_player_count: 6 },
  "England": { fifa_rating: 86, squad_value_m: 1200, home_continent: "Europe", star_player_count: 6 },
  "Brazil": { fifa_rating: 85, squad_value_m: 950, home_continent: "South America", star_player_count: 5 },
  "Portugal": { fifa_rating: 84, squad_value_m: 890, home_continent: "Europe", star_player_count: 4 },
  "Netherlands": { fifa_rating: 83, squad_value_m: 750, home_continent: "Europe", star_player_count: 3 },
  "Germany": { fifa_rating: 84, squad_value_m: 820, home_continent: "Europe", star_player_count: 4 },
  "Colombia": { fifa_rating: 81, squad_value_m: 280, home_continent: "South America", star_player_count: 2 },
  "Croatia": { fifa_rating: 82, squad_value_m: 350, home_continent: "Europe", star_player_count: 2 },
  "Morocco": { fifa_rating: 80, squad_value_m: 310, home_continent: "Africa", star_player_count: 2 },
  "Italy": { fifa_rating: 83, squad_value_m: 650, home_continent: "Europe", star_player_count: 3 },
  "Japan": { fifa_rating: 79, squad_value_m: 210, home_continent: "Asia", star_player_count: 1 },
  "Ecuador": { fifa_rating: 78, squad_value_m: 180, home_continent: "South America", star_player_count: 1 },
  "Uruguay": { fifa_rating: 81, squad_value_m: 450, home_continent: "South America", star_player_count: 3 },
  "Belgium": { fifa_rating: 82, squad_value_m: 480, home_continent: "Europe", star_player_count: 3 },
};

const defaultEnrichment = {
  fifa_rating: 75,
  squad_value_m: 100,
  home_continent: "Unknown",
  star_player_count: 0
};

const enrichedData = data.map(team => {
  const meta = enrichments[team.team] || defaultEnrichment;
  return { ...team, ...meta };
});

fs.writeFileSync(dataPath, JSON.stringify(enrichedData));
console.log('Data enriched successfully!');
