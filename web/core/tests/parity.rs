//! The Rust core against the Python package: every answer in parity.txt (written by `python web/gen_parity.py` from
//! the package itself) must come out the same, word for word, when the Rust results are printed the way the
//! package prints them.

use aaoc_core::{Account, Day, Reach, aaoc_days, aaoc_days_with_new_account, age_format, civil_from_days, days_from_civil, earliest_new_account, time_to_target};

fn day(mdy: &str) -> Day {
    let parts: Vec<u32> = mdy.split('-').map(|p| p.parse().expect("a number")).collect();
    days_from_civil(parts[2] as i32, parts[0], parts[1])
}

fn mdy(d: Day) -> String {
    let (y, m, dd) = civil_from_days(d);
    format!("{m:02}-{dd:02}-{y}")
}

fn age_text(days: f64) -> String {
    let (years, months) = age_format(days);
    format!("{years} years and {months} months")
}

fn two(args: &str) -> (i32, i32) {
    let mut it = args.split(' ').map(|p| p.parse::<i32>().expect("a number"));
    (it.next().unwrap(), it.next().unwrap())
}

#[test]
fn every_python_answer_is_reproduced() {
    let text = include_str!("parity.txt");
    let mut checked = 0;
    let mut wrong = Vec::new();
    for line in text.lines().filter(|l| !l.starts_with('#') && !l.trim().is_empty()) {
        let f: Vec<&str> = line.splitn(6, '|').collect();
        let (today, query, args, expected) = (day(f[1]), f[3], f[4], f[5]);
        let accounts: Vec<Account> = f[2]
            .split(',')
            .map(|a| {
                let (opened, closed) = a.split_once(':').unwrap();
                Account { opened: day(opened), closed: if closed == "-" { None } else { Some(day(closed)) } }
            })
            .collect();
        let got = match query {
            "now" => age_text(aaoc_days(&accounts, today).unwrap()),
            "future" => age_text(aaoc_days(&accounts, day(args)).unwrap()),
            "withnew" => {
                let (opened, measured) = args.split_once(' ').unwrap();
                age_text(aaoc_days_with_new_account(&accounts, day(opened), day(measured)).unwrap())
            }
            "target" => {
                let (ty, tm) = two(args);
                match time_to_target(&accounts, today, ty, tm) {
                    Reach::Already => format!("Target AAOC of {ty} years {tm} months already achieved"),
                    Reach::On { day, wait_years, wait_months } => format!(
                        "To reach AAOC of {ty} years {tm} months, you will need to wait {wait_years} years {wait_months} months or until {}",
                        mdy(day)
                    ),
                    Reach::Never | Reach::NoAccounts => "Target AAOC not reachable within reasonable timeframe".to_string(),
                }
            }
            "earliest" => {
                let (my, mm) = two(args);
                match earliest_new_account(&accounts, today, my, mm) {
                    Some(d) => format!("You can open a new account on {} and maintain minimum AAOC of {my} years {mm} months", mdy(d)),
                    None => "Target AAOC not reachable within reasonable timeframe".to_string(),
                }
            }
            other => panic!("unknown query {other}"),
        };
        checked += 1;
        if got != expected {
            wrong.push(format!("case {} {query} {args}\n  python: {expected}\n  rust:   {got}", f[0]));
        }
    }
    assert!(checked >= 2000, "only {checked} answers read");
    assert!(wrong.is_empty(), "{} of {checked} differ:\n{}", wrong.len(), wrong.iter().take(10).cloned().collect::<Vec<_>>().join("\n"));
}
