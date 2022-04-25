use pokemon_server;

CREATE TABLE user
(
userId INT PRIMARY KEY NOT NULL,
name VARCHAR(32) NOT NULL,
numPokemon INT NOT NULL
);

CREATE TABLE admin
(
userId INT NOT NULL,
name VARCHAR(32) NOT NULL,
FOREIGN KEY (userId) REFERENCES user(userId)
	ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE type
(
name VARCHAR(32) PRIMARY KEY NOT NULL,
advantages VARCHAR(64) NOT NULL,
disadvantages VARCHAR(64) NOT NULL
);
    
CREATE TABLE pokemon
(
pID INT auto_increment PRIMARY KEY,
pName VARCHAR(32) NOT NULL,
generation INT NOT NULL,
type VARCHAR(32) NOT NULL,
FOREIGN KEY (type) REFERENCES type(name)
	ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE powers
(
pId INT auto_increment NOT NULL,
total INT NOT NULL,
hp INT NOT NULL,
attack INT NOT NULL,
defense INT NOT NULL,
spAtk INT NOT NULL,
spDef INT NOT NULL,
speed INT NOT NULL,
FOREIGN KEY (pId) REFERENCES pokemon(pId)
	ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE item
(
name VARCHAR(32) PRIMARY KEY,
category VARCHAR(32) NOT NULL
);

CREATE TABLE team
(
teamId INT auto_increment PRIMARY KEY,
userId INT,
FOREIGN KEY (userId) REFERENCES user(userId)
	ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE teamMember
(
pId INT auto_increment NOT NULL,
teamId INT NOT NULL,
item VARCHAR(32),
level INT NOT NULL,
health INT NOT NULL,
FOREIGN KEY (pId) REFERENCES pokemon(pId)
	ON UPDATE CASCADE ON DELETE RESTRICT,
FOREIGN KEY (teamId) REFERENCES team(teamId)
	ON UPDATE CASCADE ON DELETE RESTRICT,
FOREIGN KEY (item) REFERENCES item(name)
	ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE battle
(
playerTeam INT,
opponentTeam INT,
location VARCHAR(32),
FOREIGN KEY (playerTeam) REFERENCES team(teamId)
	ON UPDATE CASCADE ON DELETE RESTRICT,
FOREIGN KEY (opponentTeam) REFERENCES team(teamId)
	ON UPDATE CASCADE ON DELETE RESTRICT
);

-- adds a teammember to team
DELIMITER //
CREATE procedure addTeamMember(pId INT, teamId INT, item VARCHAR(32), level INT, health INT)
BEGIN
INSERT INTO teamMember(pId, teamId, item, level, health) VALUES (pId, teamId, item, level, health);
END//

-- deletes a teammember from team
DELIMITER //
CREATE procedure deleteTeamMember(pId INT, teamId INT)
BEGIN
DELETE FROM teamMember WHERE teamMember.pId = pId AND teamMember.teamId = teamId;
END //

-- update a teammember from team
DELIMITER //
CREATE procedure updateTeamMember(teammemberId INT, field VARCHAR(32), newValue INT)
BEGIN
UPDATE teamMember SET field = newValue WHERE teammember.pId = teammemberId;
END //

-- compares type advantages for 2 given teams
-- returns the types of pokemons in the 2 given teams
DELIMITER //
CREATE procedure compareTeams (IN teamId1 INT, teamId2 INT)
BEGIN
SELECT advantages FROM type
INNER JOIN pokemon
ON type.type = pokemon.type
INNER JOIN teamMember
ON pokemon.pId = teamMember.pId
WHERE teamMember.teamId = teamId1 AND teamMember.teamId = teamId2;
END//

DELIMITER //
CREATE function teamTypes (teamId1 INT)
RETURNS varchar(32)
READS SQL DATA
BEGIN
SELECT type FROM type
INNER JOIN pokemon
ON type.type = pokemon.type
INNER JOIN teamMember
ON pokemon.pId = teamMember.pId
WHERE teamMember.teamId = teamId1;
END//

SELECT teamTypes(304), teamTypes(306) FROM type;

-- If less than 6 members, reccomends a team member to add
DELIMITER //
CREATE procedure reccomendTeamMember(teamId INT)
BEGIN
SELECT pId, pName FROM pokemon
INNER JOIN teamMember
ON pokemon.pId = teamMember.pId
WHERE teamMember.teamId = teamId;	
END//

-- Finds a pokemon based on a given ID 
DELIMITER //
CREATE procedure findPokemonByID(pokemonId INT)
SELECT * FROM pokemon WHERE pId = pokemonId;
BEGIN
END//

-- Finds a pokemon based on a given name
DELIMITER //
CREATE procedure findPokemonByName(pokemoneName VARCHAR(32))
SELECT * FROM pokemon WHERE pName = pokemonName;
BEGIN
END//

