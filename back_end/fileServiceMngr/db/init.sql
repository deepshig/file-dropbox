CREATE DATABASE fileServiceMgr;
use fileServiceMgr;

CREATE TABLE clients_history (
  uid INT(20),
  userName VARCHAR(30),
  fileId VARCHAR(10),
  fileName VARCHAR(30),
  activity INT(1)
);

INSERT INTO clients_history
  (uid, userName, fileId, fileName, activity)
VALUES
  (1, 'John Doe', '12345','weights_v10.m',1);




