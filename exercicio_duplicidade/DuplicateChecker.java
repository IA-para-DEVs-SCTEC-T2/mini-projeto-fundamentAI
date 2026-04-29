import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class DuplicateChecker {

    // -------------------------------------------------------------------------
    // Método original: busca duplicatas com dois loops aninhados (O(n²))
    // -------------------------------------------------------------------------
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

    // -------------------------------------------------------------------------
    // Método gerado via IA: busca duplicatas com HashSet (O(n))
    // -------------------------------------------------------------------------
    public boolean hasDuplicatesAI(List<Integer> list) {
        if (list == null || list.size() < 2) {
            return false;
        }

        Set<Integer> seen = new HashSet<>();
        for (int number : list) {
            if (!seen.add(number)) {
                return true;
            }
        }

        return false;
    }

    // -------------------------------------------------------------------------
    // Comparação entre os dois métodos
    // -------------------------------------------------------------------------
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

        System.out.println("Lista: " + numbers);
        System.out.println("[Original - O(n²)] Tem duplicatas? " + checker.hasDuplicates(numbers));
        System.out.println("[IA       - O(n) ] Tem duplicatas? " + checker.hasDuplicatesAI(numbers));

        ArrayList<Integer> semDuplicatas = new ArrayList<>();
        semDuplicatas.add(10);
        semDuplicatas.add(20);
        semDuplicatas.add(30);

        System.out.println("\nLista: " + semDuplicatas);
        System.out.println("[Original - O(n²)] Tem duplicatas? " + checker.hasDuplicates(semDuplicatas));
        System.out.println("[IA       - O(n) ] Tem duplicatas? " + checker.hasDuplicatesAI(semDuplicatas));
    }
}
