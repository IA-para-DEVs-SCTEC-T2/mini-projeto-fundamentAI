import java.util.ArrayList;

public class DuplicateChecker {
    public boolean hasDuplicates(ArrayList<Integer> list) {
        if (list == null || list.size() < 2) {
            return false;
        }

        for (int i = 0; i < list.size(); i++) {
            int currentNumber = list.get(i);

            for (int j = i + 1; j < list.size(); j++) {
                int nextNumber = list.get(j);
                if (currentNumber == nextNumber) {
                    return true;
                }
            }
        }

        return false;
    }

    public static void main(String[] args) {
        DuplicateChecker checker = new DuplicateChecker();

        ArrayList<Integer> numbers = new ArrayList<>();
        numbers.add(1);
        numbers.add(2);
        numbers.add(3);
        numbers.add(4);
        numbers.add(5);
        numbers.add(5);
        numbers.add(7);

        boolean result = checker.hasDuplicates(numbers);
        System.out.println("Has duplicates? " + result);
    }
}