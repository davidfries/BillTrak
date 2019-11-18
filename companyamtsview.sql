create view companyamts as
select company.companyid, users.userid, company.companyname, sum(amt) from bills, company, users 
where company.userid=users.userid and bills.companyid=company.companyid 
group by company.companyid, users.userid, company.companyname