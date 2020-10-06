



CREATE DATABASE fileServiceMgr;
use fileServiceMgr;

CREATE TABLE client_history1(
  id INT NOT NULL AUTO_INCREMENT,
  clientName VARCHAR(30),
  clientId  INT(10),
  fileId VARCHAR(10),
  mongo_fileId VARCHAR(30),
  fileName VARCHAR(30),
  activity INT(2),
  primary key (id)


);



INSERT INTO client_history1
  (clientName, clientId , fileId,  mongo_fileId, fileName,activity)
VALUES
  ('John Doe', '12345','333333',"hgd345",'weights_v10.m',1);

INSERT INTO client_history
  (clientName, clientId , fileId,  mongo_fileId, fileName, activity)
VALUES
  ('John Doe1', '12345','333333','weights_v10.m',1);





