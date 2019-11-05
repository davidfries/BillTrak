CREATE VIEW billdatabyuserid AS
	 SELECT users.userid,
   users.email,
    company.companyname,
	bills.billid,
    bills.amt,
    bills.duedate,
    bills.paid,
    bills.phonenum,
    bills.paymenturl,
    bills.confirmationnum
   FROM users
     JOIN company USING (userid)
     JOIN bills USING (companyid);