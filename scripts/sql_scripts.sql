select a.email, a.phone, b.email_opt_in, b.phone_opt_in
from personal_details a
left join 
"temp".opt_in_status b
on a.email = b.email_id;
