//! The AAOC (average age of credit) planner's math, ported from the Python package (`aaoc_project`) so the web view
//! runs it in the browser as WebAssembly. Every result matches the Python code: `tests/parity.rs` checks this crate
//! against answers the Python package itself produced (`web/gen_parity.py`).
//!
//! Dates are whole days since 1970-01-01 (`Day`), so all arithmetic is on integers until the average, which is done
//! in `f64` in the same order as Python so the floats agree bit for bit.

/// Days since 1970-01-01.
pub type Day = i32;

/// An account's dates. `closed` is `None` while the account is open.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Account {
    pub opened: Day,
    pub closed: Option<Day>,
}

/// Days per year the Python package divides by.
pub const DAYS_PER_YEAR: f64 = 365.25;
/// How many monthly steps the planner tries before giving up (the Python package's `while iterations < 9999`).
pub const MAX_STEPS: u32 = 9999;

// ---------------------------------------------------------------------------------------------------------------
// Calendar (proleptic Gregorian), after Howard Hinnant's days_from_civil / civil_from_days.
// ---------------------------------------------------------------------------------------------------------------

/// The day number of a calendar date (`month` 1-12, `day` 1-31).
pub fn days_from_civil(year: i32, month: u32, day: u32) -> Day {
    let y = if month <= 2 { year - 1 } else { year };
    let era = if y >= 0 { y } else { y - 399 } / 400;
    let yoe = (y - era * 400) as u32; // [0, 399]
    let mp = (month + 9) % 12; // March = 0
    let doy = (153 * mp + 2) / 5 + day - 1; // [0, 365]
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy; // [0, 146096]
    era * 146097 + doe as i32 - 719468
}

/// The calendar date `(year, month, day)` of a day number.
pub fn civil_from_days(z: Day) -> (i32, u32, u32) {
    let z = z + 719468;
    let era = if z >= 0 { z } else { z - 146096 } / 146097;
    let doe = (z - era * 146097) as u32; // [0, 146096]
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365; // [0, 399]
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100); // [0, 365]
    let mp = (5 * doy + 2) / 153; // [0, 11]
    let day = doy - (153 * mp + 2) / 5 + 1;
    let month = if mp < 10 { mp + 3 } else { mp - 9 };
    let year = yoe as i32 + era * 400 + if month <= 2 { 1 } else { 0 };
    (year, month, day)
}

fn is_leap(year: i32) -> bool {
    (year % 4 == 0 && year % 100 != 0) || year % 400 == 0
}

fn days_in_month(year: i32, month: u32) -> u32 {
    match month {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        _ if is_leap(year) => 29,
        _ => 28,
    }
}

/// `day` moved by `months` calendar months, the day of the month clamped to the target month's length
/// (Jan 31 + 1 month = Feb 28 or 29). The Python package's `add_months`.
pub fn add_months(day: Day, months: i32) -> Day {
    let (y, m, d) = civil_from_days(day);
    let index = m as i32 - 1 + months;
    let year = y + index.div_euclid(12);
    let month = index.rem_euclid(12) as u32 + 1;
    days_from_civil(year, month, d.min(days_in_month(year, month)))
}

// ---------------------------------------------------------------------------------------------------------------
// Ages and the average
// ---------------------------------------------------------------------------------------------------------------

/// An account's age in days on `as_of`: a closed account stops aging on the day it closed. (`Account.age_on`.)
pub fn age_on(account: &Account, as_of: Day) -> i32 {
    match account.closed {
        Some(closed) if as_of > closed => closed - account.opened,
        _ => as_of - account.opened,
    }
}

/// The average age in days, on `as_of`, of the accounts opened by then, or `None` if none was.
/// (`Planner._calculate_aaoc_decimal` before its division by 365.25.)
pub fn aaoc_days(accounts: &[Account], as_of: Day) -> Option<f64> {
    let mut total: i64 = 0;
    let mut count: i64 = 0;
    for account in accounts.iter().filter(|a| a.opened <= as_of) {
        total += age_on(account, as_of) as i64;
        count += 1;
    }
    if count == 0 { None } else { Some(total as f64 / count as f64) }
}

/// The average age in years (`days / 365.25`).
pub fn aaoc_years(accounts: &[Account], as_of: Day) -> Option<f64> {
    aaoc_days(accounts, as_of).map(|days| days / DAYS_PER_YEAR)
}

/// The average age in days if a new account were opened on `opened_new`, measured on `as_of`.
pub fn aaoc_days_with_new_account(accounts: &[Account], opened_new: Day, as_of: Day) -> Option<f64> {
    let mut with_new = accounts.to_vec();
    with_new.push(Account { opened: opened_new, closed: None });
    aaoc_days(&with_new, as_of)
}

/// A number of days as whole years and months, the way the Python package prints it (`age_format`): negative
/// counts as zero, months rounded with Python's `round` (half to even), and 12 months carried into a year.
/// The rounding rule shows only for 32 or more accounts: an average of whole-day ages lands exactly on half a
/// month only when 96 x total = odd x 1461 x count, which needs 32 | count (e.g. 32 accounts, 487 days in all:
/// Python says 0 months, half-away-from-zero would say 1). tests/parity.txt includes such portfolios.
pub fn age_format(total_days: f64) -> (i32, i32) {
    let days = if total_days < 0.0 { 0.0 } else { total_days };
    let years_float = days / DAYS_PER_YEAR;
    let mut years = years_float.trunc() as i32;
    let mut months = ((years_float - years as f64) * 12.0).round_ties_even() as i32;
    if months == 12 {
        years += 1;
        months = 0;
    }
    (years, months)
}

// ---------------------------------------------------------------------------------------------------------------
// The planner's two searches
// ---------------------------------------------------------------------------------------------------------------

/// The answer to "when will my AAOC reach the target?".
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Reach {
    /// The average is already at or above the target today.
    Already,
    /// The first monthly step on which it is: the date, and the wait as the Python package states it.
    On { day: Day, wait_years: i32, wait_months: i32 },
    /// Not within 9,999 monthly steps.
    Never,
    /// No account is open by today.
    NoAccounts,
}

/// Steps forward a month at a time from `today` (each step from the last, as the Python package does, so a
/// clamped day of the month stays clamped) until the average age reaches `target_years + target_months / 12`.
/// (`Planner.time_to_target_aaoc`.)
pub fn time_to_target(accounts: &[Account], today: Day, target_years: i32, target_months: i32) -> Reach {
    let target = target_years as f64 + target_months as f64 / 12.0;
    match aaoc_years(accounts, today) {
        None => return Reach::NoAccounts,
        Some(now) if now >= target => return Reach::Already,
        _ => {}
    }
    let mut day = today;
    for _ in 0..MAX_STEPS {
        match aaoc_years(accounts, day) {
            None => return Reach::NoAccounts,
            Some(years) if years >= target => {
                let waited = day - today;
                return Reach::On { day, wait_years: waited.div_euclid(365), wait_months: waited.rem_euclid(365) / 30 };
            }
            _ => {}
        }
        day = add_months(day, 1);
    }
    Reach::Never
}

/// The first monthly step from `today` on which a brand-new account opened that day still leaves the average at
/// or above `min_years + min_months / 12`, or `None` if none within 9,999 steps.
/// (`Planner.earliest_new_account_date`.)
pub fn earliest_new_account(accounts: &[Account], today: Day, min_years: i32, min_months: i32) -> Option<Day> {
    let minimum = min_years as f64 + min_months as f64 / 12.0;
    let mut day = today;
    for _ in 0..MAX_STEPS {
        if let Some(days) = aaoc_days_with_new_account(accounts, day, day) {
            if days / DAYS_PER_YEAR >= minimum {
                return Some(day);
            }
        }
        day = add_months(day, 1);
    }
    None
}

// ---------------------------------------------------------------------------------------------------------------
// WebAssembly exports: a hand-written boundary, no bindings crate. The page writes accounts into memory it gets
// from `alloc` as pairs of i32 (opened, closed or NO_CLOSE) and calls the functions below with a pointer and a count.
// ---------------------------------------------------------------------------------------------------------------

/// The `closed` value for an open account at the boundary.
pub const NO_CLOSE: i32 = i32::MIN;
/// Day results that are not days.
pub const ALREADY: i32 = i32::MIN;
pub const NEVER: i32 = i32::MIN + 1;
pub const NO_ACCOUNTS: i32 = i32::MIN + 2;

fn accounts_at(ptr: *const i32, count: usize) -> Vec<Account> {
    if ptr.is_null() || count == 0 {
        return Vec::new();
    }
    // SAFETY: the page passes a pointer it got from `alloc(2 * count)` and wrote 2 * count values into.
    let raw = unsafe { std::slice::from_raw_parts(ptr, count * 2) };
    raw.chunks_exact(2).map(|p| Account { opened: p[0], closed: if p[1] == NO_CLOSE { None } else { Some(p[1]) } }).collect()
}

/// Room for `count` i32 values, for the page to write accounts into.
#[unsafe(no_mangle)]
pub extern "C" fn alloc(count: usize) -> *mut i32 {
    let mut buffer = vec![0i32; count.max(1)];
    let ptr = buffer.as_mut_ptr();
    std::mem::forget(buffer);
    ptr
}

/// Returns memory from `alloc`.
#[unsafe(no_mangle)]
pub extern "C" fn dealloc(ptr: *mut i32, count: usize) {
    if !ptr.is_null() {
        // SAFETY: `ptr` and `count` are exactly what `alloc` returned and was asked for.
        unsafe { drop(Vec::from_raw_parts(ptr, count.max(1), count.max(1))) };
    }
}

#[unsafe(no_mangle)]
pub extern "C" fn wasm_days_from_civil(year: i32, month: u32, day: u32) -> Day {
    days_from_civil(year, month, day)
}

/// The date of a day number packed as `year * 10000 + month * 100 + day`.
#[unsafe(no_mangle)]
pub extern "C" fn wasm_civil_from_days(day: Day) -> i32 {
    let (y, m, d) = civil_from_days(day);
    y * 10000 + m as i32 * 100 + d as i32
}

#[unsafe(no_mangle)]
pub extern "C" fn wasm_add_months(day: Day, months: i32) -> Day {
    add_months(day, months)
}

/// The average age in days on `as_of`, or NaN when no account is open by then.
#[unsafe(no_mangle)]
pub extern "C" fn wasm_aaoc_days(ptr: *const i32, count: usize, as_of: Day) -> f64 {
    aaoc_days(&accounts_at(ptr, count), as_of).unwrap_or(f64::NAN)
}

#[unsafe(no_mangle)]
pub extern "C" fn wasm_aaoc_days_with_new_account(ptr: *const i32, count: usize, opened_new: Day, as_of: Day) -> f64 {
    aaoc_days_with_new_account(&accounts_at(ptr, count), opened_new, as_of).unwrap_or(f64::NAN)
}

/// `age_format` packed as `years * 100 + months`.
#[unsafe(no_mangle)]
pub extern "C" fn wasm_age_format(total_days: f64) -> i32 {
    let (years, months) = age_format(total_days);
    years * 100 + months
}

/// The day the target is reached, or ALREADY, NEVER or NO_ACCOUNTS.
#[unsafe(no_mangle)]
pub extern "C" fn wasm_time_to_target(ptr: *const i32, count: usize, today: Day, years: i32, months: i32) -> Day {
    match time_to_target(&accounts_at(ptr, count), today, years, months) {
        Reach::Already => ALREADY,
        Reach::On { day, .. } => day,
        Reach::Never => NEVER,
        Reach::NoAccounts => NO_ACCOUNTS,
    }
}

/// The Python package's stated wait between two days, packed as `years * 100 + months`.
#[unsafe(no_mangle)]
pub extern "C" fn wasm_wait(today: Day, day: Day) -> i32 {
    let waited = day - today;
    waited.div_euclid(365) * 100 + waited.rem_euclid(365) / 30
}

/// The earliest day to open a new account and keep the minimum, or NEVER.
#[unsafe(no_mangle)]
pub extern "C" fn wasm_earliest_new_account(ptr: *const i32, count: usize, today: Day, years: i32, months: i32) -> Day {
    earliest_new_account(&accounts_at(ptr, count), today, years, months).unwrap_or(NEVER)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn calendar_round_trips_every_day_from_1900_to_2200() {
        let start = days_from_civil(1900, 1, 1);
        let end = days_from_civil(2200, 12, 31);
        for day in start..=end {
            let (y, m, d) = civil_from_days(day);
            assert_eq!(days_from_civil(y, m, d), day);
        }
        assert_eq!(days_from_civil(1970, 1, 1), 0);
        assert_eq!(civil_from_days(days_from_civil(2024, 2, 29)), (2024, 2, 29));
    }

    #[test]
    fn add_months_clamps_to_the_month_end() {
        let jan31 = days_from_civil(2024, 1, 31);
        assert_eq!(civil_from_days(add_months(jan31, 1)), (2024, 2, 29));
        assert_eq!(civil_from_days(add_months(days_from_civil(2023, 1, 31), 1)), (2023, 2, 28));
        assert_eq!(civil_from_days(add_months(days_from_civil(2023, 12, 15), 1)), (2024, 1, 15));
        assert_eq!(civil_from_days(add_months(days_from_civil(2024, 3, 31), -1)), (2024, 2, 29));
    }

    #[test]
    fn closed_accounts_stop_aging() {
        let a = Account { opened: 100, closed: Some(150) };
        assert_eq!(age_on(&a, 120), 20);
        assert_eq!(age_on(&a, 400), 50);
        assert_eq!(age_on(&Account { opened: 100, closed: None }, 400), 300);
    }

    #[test]
    fn the_average_ignores_accounts_not_yet_opened() {
        let accounts = [Account { opened: 0, closed: None }, Account { opened: 1000, closed: None }];
        assert_eq!(aaoc_days(&accounts, 500), Some(500.0));
        assert_eq!(aaoc_days(&accounts, 1500), Some(1000.0));
        assert_eq!(aaoc_days(&accounts, -1), None);
    }

    #[test]
    fn age_format_clamps_negatives_and_carries_twelve_months() {
        assert_eq!(age_format(0.0), (0, 0));
        assert_eq!(age_format(-5.0), (0, 0));
        assert_eq!(age_format(365.25), (1, 0));
        assert_eq!(age_format(365.25 * 1.99), (2, 0)); // 11.88 months rounds to 12, carried into the year
        assert_eq!(age_format(365.25 * 2.5), (2, 6));
    }

    #[test]
    fn time_to_target_and_earliest_account() {
        let today = days_from_civil(2026, 1, 31);
        let accounts = [Account { opened: days_from_civil(2020, 1, 31), closed: None }];
        assert_eq!(time_to_target(&accounts, today, 5, 0), Reach::Already);
        match time_to_target(&accounts, today, 7, 0) {
            Reach::On { day, wait_years, wait_months } => {
                assert!(aaoc_years(&accounts, day).unwrap() >= 7.0);
                assert_eq!((wait_years, wait_months), (1, 0));
            }
            other => panic!("{other:?}"),
        }
        assert_eq!(time_to_target(&[], today, 1, 0), Reach::NoAccounts);
        let day = earliest_new_account(&accounts, today, 3, 0).unwrap();
        assert!(aaoc_days_with_new_account(&accounts, day, day).unwrap() / DAYS_PER_YEAR >= 3.0);
        assert_eq!(earliest_new_account(&accounts, today, 1000, 0), None);
    }

    #[test]
    fn the_boundary_reads_accounts_and_sentinels() {
        let buffer = alloc(4);
        unsafe {
            *buffer = 0;
            *buffer.add(1) = NO_CLOSE;
            *buffer.add(2) = 100;
            *buffer.add(3) = 150;
        }
        assert_eq!(wasm_aaoc_days(buffer, 2, 400), (400.0 + 50.0) / 2.0);
        assert!(wasm_aaoc_days(buffer, 2, -1).is_nan());
        assert_eq!(wasm_age_format(365.25 * 2.5), 206);
        assert_eq!(wasm_civil_from_days(days_from_civil(2026, 11, 25)), 20261125);
        assert_eq!(wasm_time_to_target(buffer, 0, 0, 1, 0), NO_ACCOUNTS);
        dealloc(buffer, 4);
    }
}
