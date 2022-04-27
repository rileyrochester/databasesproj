drop database pokemon_server;
create database pokemon_server;
use pokemon_server;

CREATE TABLE IF NOT EXISTS user
(
userId INT PRIMARY KEY NOT NULL,
name VARCHAR(32) NOT NULL,
numPokemon INT NOT NULL
);

CREATE TABLE IF NOT EXISTS admin
(
userId INT NOT NULL,
name VARCHAR(32) NOT NULL,
FOREIGN KEY (userId) REFERENCES user(userId)
	ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS type
(
name VARCHAR(32) PRIMARY KEY NOT NULL,
advantages VARCHAR(64) NOT NULL,
disadvantages VARCHAR(64) NOT NULL,
advantageScore INT NOT NULL
);
    
CREATE TABLE IF NOT EXISTS pokemon
(
pID INT auto_increment PRIMARY KEY,
pName VARCHAR(32) NOT NULL,
generation INT NOT NULL,
type VARCHAR(32) NOT NULL,
FOREIGN KEY (type) REFERENCES type(name)
	ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS powers
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

CREATE TABLE IF NOT EXISTS item
(
name VARCHAR(32) PRIMARY KEY,
category VARCHAR(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS team
(
teamId INT auto_increment PRIMARY KEY,
userId INT,
FOREIGN KEY (userId) REFERENCES user(userId)
	ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS teamMember
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

CREATE TABLE IF NOT EXISTS battle
(
playerTeam INT,
opponentTeam INT,
location VARCHAR(32),
FOREIGN KEY (playerTeam) REFERENCES team(teamId)
	ON UPDATE CASCADE ON DELETE RESTRICT,
FOREIGN KEY (opponentTeam) REFERENCES team(teamId)
	ON UPDATE CASCADE ON DELETE RESTRICT
);

-- creates a user
DELIMITER //
CREATE procedure createUser(userID INT, userName VARCHAR(32))
BEGIN
INSERT INTO user(userId, name, numPokemon) VALUES (userID, userName, 0);
END//

-- creates a team
DELIMITER //
CREATE procedure createTeam(userId INT)
BEGIN
INSERT INTO team(teamId, userId) VALUES (userId);
END//

-- adds a teammember to team
DELIMITER //
CREATE procedure addTeamMember(pId INT, teamId INT, item VARCHAR(32), level INT)
BEGIN
DECLARE healthTemp INT;

SELECT hp INTO healthTemp FROM powers
WHERE pId = pId;

INSERT INTO teamMember(pId, teamId, item, level, health) VALUES (pId, teamId, item, level, healthTemp);
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
delimiter ;
drop procedure if exists findPokemonByID;
DELIMITER //
CREATE procedure findPokemonByID(pokemonId INT)
BEGIN
SELECT * FROM pokemon WHERE pId = pokemonId;
END//

-- Finds a pokemon's powers based on a given ID 
delimiter ;
drop procedure if exists findPokemonPowersByID;
DELIMITER //
CREATE procedure findPokemonPowersByID(pokemonId INT)
BEGIN
SELECT * FROM powers WHERE pId = pokemonId;
END//

-- Finds a pokemon based on a given name 
delimiter ;
drop procedure if exists findPokemonByName;
DELIMITER //
CREATE procedure findPokemonByName(pokemonName VARCHAR(32))
BEGIN
SELECT * FROM pokemon WHERE pName = pokemonName;
END//
select * from pokemon;