<?php
require_once "Mail.php";

/* Parse credentials file for email username and password */
$section_found = false;

$lines = file('../../private/credentials');
if ($lines == false) {
    return;
}

/*************************************************
 *   Credentials file should look like
 *   ::email::
 *   [username] = me
 *   [password] = hungry
 **************************************************/
foreach ($lines as $line_num => $line) {
    if ($section_found == false) {
        if (strcasecmp(trim($line), "::email::") == 0) {
            $section_found = true;
        }
    }
    else {
        $field = trim(strtok($line,"="));
        if (strcasecmp($field, "[password]") == 0) {
            $password = trim(strtok("="));
        }
        else if (strcasecmp($field, "[username]") == 0) {
            $username = trim(strtok("="));
        }
    }
}

if (empty($username) || empty($password)) {
    return;
}

$from    = "me@gmail.com";
$to      = "9050001111@txt.windmobile.ca";
$subject = "[$server] Notification";
$body    = "Hello From Raspberry Pi!";

$config=array(
    'host'      => 'ssl://smtp.googlemail.com',
    'port'      => 465,
    'auth'      => true,
    'username'  => $username,
    'password'  => $password,
);

$headers=array(
    'From'      => $from,
    'To'        => $to,
    'Subject'   => $subject
);

$smtp = Mail::factory('smtp',$config);

$mail = $smtp->send($to, $headers, $body);

if(!(PEAR::isError($mail))) {
    echo "Mail went successfully!";
}
else {
    echo $mail->getMessage();
}
?>
