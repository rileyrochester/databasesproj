-- drop database pokemon_server;
create database pokemon_server;

use pokemon_server;

CREATE TABLE user
(
userId INT auto_increment PRIMARY KEY NOT NULL,
name VARCHAR(32) NOT NULL,
numPokemon INT NOT NULL
);

CREATE TABLE admin
(
userId INT auto_increment NULL,
name VARCHAR(32) NOT NULL,
FOREIGN KEY (userId) REFERENCES user(userId)
	ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE type
(
name VARCHAR(32) PRIMARY KEY NOT NULL,
advantages VARCHAR(64) NOT NULL,
disadvantages VARCHAR(64) NOT NULL,
advantageScore INT NOT NULL
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

-- gets items
DELIMITER //
CREATE procedure getItems()
BEGIN
select * from item;
END//

-- creates a user
DELIMITER //
CREATE procedure createUser(uname VARCHAR(32))
BEGIN
INSERT INTO user(name, numPokemon) VALUES(uname, 0);
END//

-- gets a user's id from name 
DELIMITER //
CREATE procedure getUserIDFromName(name VARCHAR(32))
BEGIN
SELECT userId FROM user WHERE user.name = name;
END//

-- creates a team
DELIMITER //
CREATE procedure createTeam(userId INT)
BEGIN
INSERT INTO team(userId) VALUES (userId);
select teamId from team where team.userId = userId;
END//

-- adds a teammember to team
DELIMITER //
CREATE procedure addTeamMember(pId INT, teamId INT, item VARCHAR(32), level INT)
BEGIN
DECLARE healthTemp INT;
DECLARE userIdTemp INT;

SELECT hp INTO healthTemp FROM powers
WHERE pId = pId;

INSERT INTO teamMember(pId, teamId, item, level, health) VALUES (pId, teamId, item, level, healthTemp);

SELECT teamId INTO userIdTemp FROM team
INNER JOIN user
ON team.userId = user.userId
WHERE team.teamId = teamId;

UPDATE user SET numPokemon = (numPokemon + 1) WHERE userId = userIdTemp;

END//

-- deletes a teammember from team
DELIMITER //
CREATE procedure deleteTeamMember(pId INT, teamId INT)
BEGIN
DELETE FROM teamMember WHERE teamMember.pId = pId AND teamMember.teamId = teamId;
END //

-- update a teammember from team
DELIMITER //
CREATE procedure updateTeamMember(teamId INT, teammemberId INT, newValue INT)
BEGIN
UPDATE teamMember SET teamMember.level = newValue WHERE teamMember.teamId = teamId AND teammember.pId = teammemberId;
END //

-- creates a battle
DELIMITER //
CREATE procedure createBattle(team1 INT, team2 INT, location VARCHAR(32))
BEGIN
INSERT INTO battle(playerTeam, opponentTeam, location) VALUES (team1, team2, location); 
END//

-- compares type advantages for 2 given teams
DELIMITER //
CREATE function compareTeams (teamId1 INT, teamId2 INT) RETURNS VARCHAR(32) READS SQL DATA
BEGIN

DECLARE avgScore1 INT;
DECLARE avgScore2 INT;
DECLARE result VARCHAR(32);

SELECT avg(advantageScore) INTO avgScore1 FROM type
INNER JOIN pokemon
ON type.type = pokemon.type
INNER JOIN teamMember
ON pokemon.pId = teamMember.pId
WHERE teamMember.teamId = teamId1;

SELECT avg(advantageScore) INTO avgScore2 FROM type
INNER JOIN pokemon
ON type.type = pokemon.type
INNER JOIN teamMember
ON pokemon.pId = teamMember.pId
WHERE teamMember.teamId = teamId2;

IF(avgScore1 > avgScore2)
	THEN SET result = 'Team 1 has the advantage';
ELSE
	SET result = 'Team 2 has the advantage';
END IF;

RETURN result;
END//

-- If less than 6 members, reccomends a team member to add
DELIMITER //
CREATE function reccomendTeamMember(teamId INT) RETURNS VARCHAR(32) READS SQL DATA
BEGIN

DECLARE numTeamMembers INT;
DECLARE pokemonName VARCHAR(32);
DECLARE result VARCHAR(32);

SELECT count(teamId) INTO numTeamMembers FROM teamMember
WHERE teamId = teamId;

IF (numTeamMembers = 6)
	THEN SET result = 'Your team is already full';
ELSE
    SELECT max(total), pokemon.pName INTO pokemonName FROM powers
	INNER JOIN teamMembers
    ON powers.pId = teamMembers.pId
    INNER JOIN pokemon
    ON teamMembers.pId = pokemon.pId;
    
    SET result = 'Add ' + pokemonName + ' to your team to increase your power';
END IF;

RETURN result;
END//

-- Finds a pokemon based on a given ID 
DELIMITER //
CREATE procedure findPokemonByID(pokemonId INT)
BEGIN
SELECT * FROM pokemon WHERE pId = pokemonId;
END//

-- Finds a pokemon based on a given name
DELIMITER //
CREATE procedure findPokemonByName(pokemonName VARCHAR(32))
BEGIN
SELECT * FROM pokemon WHERE pName = pokemonName;
END//

-- Finds a pokemons powers based on a given ID
DELIMITER //
CREATE procedure findPokemonPowersByID(pokemonId INT)
BEGIN
SELECT * FROM powers where pId = pokemonId;
END//
