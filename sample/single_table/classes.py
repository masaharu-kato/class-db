import datetime
import typing

class Test:
    name: str

class Employee:
    birth_date: datetime.date
    first_name: str(14)
    last_name : str(16)
    gender    : Test
    hire_date : datetime.date


def main():
    print(Employee.__annotations__)
    print(typing.get_type_hints(Employee))


if __name__ == "__main__":
    main()
