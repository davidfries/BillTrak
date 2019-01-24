CREATE VIEW billdatabyuserid AS
	SELECT users.userid,company.companyname,bills.amt,bills.duedate
	FROM users join company USING(userid)
	join bills using(companyid)