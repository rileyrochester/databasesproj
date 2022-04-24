use pokemon_server;

SELECT * FROM pokemons WHERE `#` = 4;


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

CREATE TABLE teamMember
(
pId INT auto_increment NOT NULL,
item VARCHAR(32),
level INT NOT NULL,
health INT NOT NULL,
FOREIGN KEY (pId) REFERENCES pokemon(pId)
	ON UPDATE CASCADE ON DELETE RESTRICT,
FOREIGN KEY (item) REFERENCES item(name)
	ON UPDATE CASCADE ON DELETE RESTRICT
);
    
CREATE TABLE team
(
teamId INT auto_increment PRIMARY KEY,
teamMember1 INT NOT NULL,
teamMember2 INT,
teamMember3 INT,
teamMember4 INT,
teamMember5 INT,
teamMember6 INT
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
CREATE procedure addTeamMember(teammemberId INT)
BEGIN
INSERT INTO team (pId) VALUES (teammemberId);
END//

-- deletes a teammember from team
DELIMITER //
CREATE procedure deleteTeamMember(teammemberId INT)
BEGIN
DELETE FROM team WHERE teammember.pId = teammemberId;
END //

-- update a teammember from team
DELIMITER //
CREATE procedure updateTeamMember(teammemberId INT, field VARCHAR(32), newValue INT)
BEGIN
UPDATE teammember SET field = newValue WHERE teammember.pId = teammemberId;
END //

-- compares type advantages for 2 given teams
DELIMITER //
CREATE procedure compare (IN teamId1 INT, teamId2 INT)
BEGIN
SELECT teamMember1, teamMember2, teamMember3, teamMember4, teamMember5, teamMember6 FROM team
INNER JOIN
WHERE teamId = 456,
teamMember
END//

-- If less than 6 members, reccomends a team member to add

function to read pokedex -- find by ID AND NAME
