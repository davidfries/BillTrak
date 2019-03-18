CREATE VIEW billdatabyuserid AS
	 SELECT users.userid,
    company.companyname,
	bills.billid,
    bills.amt,
    bills.duedate,
    bills.phonenum,
    bills.paymenturl
   FROM users
     JOIN company USING (userid)
     JOIN bills USING (companyid);