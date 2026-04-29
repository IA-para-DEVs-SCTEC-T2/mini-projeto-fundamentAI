import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class DuplicateChecker {

    // -------------------------------------------------------------------------
    // Método original: busca duplicatas com dois loops aninhados (O(n²))
    // -------------------------------------------------------------------------
    public boolean hasDuplicates(ArrayList<Integer> list) {
        if (list == null || list.size() < 2) {
            return false;
        }

        Set<Integer> seen = new HashSet<>();
        for (int i = 0; i < list.size(); i++) {
            int currentNumber = list.get(i);
            if (!seen.add(currentNumber)) {
                return true;
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
    // Método gerado via IA (variação): conta duplicatas no total e por número
    // Retorna um Map onde a chave é o número e o valor é quantas vezes ele
    // aparece a mais (ocorrências - 1). Apenas números duplicados são incluídos.
    // -------------------------------------------------------------------------
    public Map<Integer, Integer> countDuplicatesAI(List<Integer> list) {
        Map<Integer, Integer> frequency = new HashMap<>();
        Map<Integer, Integer> duplicates = new HashMap<>();

        if (list == null) {
            return duplicates;
        }

        // Conta a frequência de cada número
        for (int number : list) {
            frequency.put(number, frequency.getOrDefault(number, 0) + 1);
        }

        // Filtra apenas os que aparecem mais de uma vez
        for (Map.Entry<Integer, Integer> entry : frequency.entrySet()) {
            if (entry.getValue() > 1) {
                // Armazena quantas vezes o número se repetiu além da primeira ocorrência
                duplicates.put(entry.getKey(), entry.getValue() - 1);
            }
        }

        return duplicates;
    }

    // Imprime o relatório de duplicatas de uma lista
    private static void printDuplicateReport(DuplicateChecker checker, List<Integer> list, String label) {
        System.out.println("=== " + label + " ===");
        System.out.println("Lista: " + list);

        Map<Integer, Integer> duplicates = checker.countDuplicatesAI(list);

        if (duplicates.isEmpty()) {
            System.out.println("Nenhuma duplicata encontrada.");
        } else {
            int totalDuplicates = duplicates.values().stream().mapToInt(Integer::intValue).sum();
            System.out.println("Total de ocorrências duplicadas: " + totalDuplicates);
            System.out.println("Detalhamento por número:");
            duplicates.entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .forEach(e -> System.out.printf("  Número %d → aparece %d vez(es) a mais%n",
                        e.getKey(), e.getValue()));
        }
        System.out.println();
    }

    // -------------------------------------------------------------------------
    // Testes e comparação entre os métodos
    // -------------------------------------------------------------------------
    public static void main(String[] args) {
        DuplicateChecker checker = new DuplicateChecker();

        // --- Comparação original vs IA (comportamento booleano) ---
        System.out.println("========== COMPARAÇÃO: Original vs IA ==========\n");

        ArrayList<Integer> numbers = new ArrayList<>();
        numbers.add(1); numbers.add(2); numbers.add(3);
        numbers.add(4); numbers.add(5); numbers.add(5); numbers.add(7);

        System.out.println("Lista: " + numbers);
        System.out.println("[Original - O(n²)] Tem duplicatas? " + checker.hasDuplicates(numbers));
        System.out.println("[IA       - O(n) ] Tem duplicatas? " + checker.hasDuplicatesAI(numbers));

        ArrayList<Integer> semDuplicatas = new ArrayList<>();
        semDuplicatas.add(10); semDuplicatas.add(20); semDuplicatas.add(30);

        System.out.println("\nLista: " + semDuplicatas);
        System.out.println("[Original - O(n²)] Tem duplicatas? " + checker.hasDuplicates(semDuplicatas));
        System.out.println("[IA       - O(n) ] Tem duplicatas? " + checker.hasDuplicatesAI(semDuplicatas));

        // --- Testes do novo método: contagem de duplicatas ---
        System.out.println("\n========== CONTAGEM DE DUPLICATAS (IA) ==========\n");

        // Cenário 1: uma duplicata simples
        printDuplicateReport(checker,
            List.of(1, 2, 3, 4, 5, 5, 7),
            "Cenário 1 - Uma duplicata simples");

        // Cenário 2: múltiplos números duplicados
        printDuplicateReport(checker,
            List.of(1, 2, 2, 3, 3, 3, 4, 5, 5),
            "Cenário 2 - Múltiplos números duplicados");

        // Cenário 3: um número repetido muitas vezes
        printDuplicateReport(checker,
            List.of(7, 7, 7, 7, 7),
            "Cenário 3 - Um número repetido muitas vezes");

        // Cenário 4: sem nenhuma duplicata
        printDuplicateReport(checker,
            List.of(10, 20, 30, 40),
            "Cenário 4 - Sem duplicatas");

        // Cenário 5: lista com um único elemento
        printDuplicateReport(checker,
            List.of(42),
            "Cenário 5 - Lista com um único elemento");

        // Cenário 6: lista vazia
        printDuplicateReport(checker,
            List.of(),
            "Cenário 6 - Lista vazia");

        // Cenário 7: lista nula
        printDuplicateReport(checker,
            null,
            "Cenário 7 - Lista nula");

        // Cenário 8: todos os elementos iguais
        printDuplicateReport(checker,
            List.of(9, 9, 9, 9),
            "Cenário 8 - Todos os elementos iguais");

        // Cenário 9: números negativos e positivos misturados com duplicatas
        printDuplicateReport(checker,
            List.of(-3, -1, 0, -1, 2, 2, -3, 5),
            "Cenário 9 - Negativos e positivos com duplicatas");
    }
}
