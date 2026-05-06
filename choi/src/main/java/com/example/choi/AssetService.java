@Service
@RequiredArgsConstructor
public class AssetService {

    private final UserRepository userRepository; // JPA 레포지토리
    private final WebClient webClient = WebClient.builder().build();

    // 은행 URL 설정
    private final Map<String, String> BANK_URLS = Map.of(
            "국민은행", "http://127.0.0.1:8001/accounts",
            "하나은행", "http://127.0.0.1:8002/accounts",
            "누리은행", "http://127.0.0.1:8003/accounts"
    );

    public Mono<Map<String, Object>> getIntegratedAssets(String userEmail) {
        // 1. 유저 조회
        User user = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "사용자를 찾을 수 없습니다."));

        String targetUuid = user.getUserId().toString();

        // 2. 모든 은행에 대한 비동기 요청 생성 (asyncio.gather 역할)
        List<Mono<Map<String, Object>>> tasks = BANK_URLS.entrySet().stream()
                .map(entry -> fetchBankData(entry.getKey(), entry.getValue(), targetUuid))
                .collect(Collectors.toList());

        // 3. 모든 응답을 합산 (Zip 사용)
        return Mono.zip(tasks, responses -> {
            long totalBalance = 0;
            List<Map<String, Object>> allAccounts = new ArrayList<>();
            List<Map<String, Object>> allCards = new ArrayList<>();
            List<Object> debugInfo = new ArrayList<>();

            for (Object obj : responses) {
                Map<String, Object> res = (Map<String, Object>) obj;
                debugInfo.add(res);

                if ("success".equals(res.get("status"))) {
                    // 계좌 처리
                    List<Map<String, Object>> accounts = (List<Map<String, Object>>) res.get("accounts");
                    for (Map<String, Object> acc : accounts) {
                        totalBalance += ((Number) acc.getOrDefault("balance", 0)).longValue();
                        acc.put("bank_origin", res.get("bank"));
                        allAccounts.add(acc);
                    }
                    // 카드 처리
                    List<Map<String, Object>> cards = (List<Map<String, Object>>) res.get("cards");
                    for (Map<String, Object> card : cards) {
                        card.put("bank_origin", res.get("bank"));
                        allCards.add(card);
                    }
                }
            }

            // 결과 맵 구성
            Map<String, Object> result = new HashMap<>();
            result.put("user_name", user.getUsername());
            result.put("user_email", user.getEmail());
            result.put("total_balance", totalBalance);
            result.put("account_count", allAccounts.size());
            result.put("card_count", allCards.size());
            result.put("details", allAccounts);
            result.put("cards", allCards);
            result.put("debug_info", debugInfo);
            return result;
        });
    }

    private Mono<Map<String, Object>> fetchBankData(String bankName, String url, String userId) {
        // 계좌와 카드를 동시에 호출 (asyncio.gather와 동일한 로직)
        Mono<List<Map<String, Object>>> accTask = webClient.get()
                .uri(url + "/accounts/" + userId)
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<List<Map<String, Object>>>() {})
                .onErrorReturn(Collections.emptyList());

        Mono<List<Map<String, Object>>> cardTask = webClient.get()
                .uri(url + "/cards/" + userId)
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<List<Map<String, Object>>>() {})
                .onErrorReturn(Collections.emptyList());

        return Mono.zip(accTask, cardTask, (accounts, cards) -> {
            Map<String, Object> map = new HashMap<>();
            map.put("bank", bankName);
            map.put("accounts", accounts);
            map.put("cards", cards);
            map.put("status", "success");
            return map;
        }).onErrorResume(e -> Mono.just(Map.of(
                "bank", bankName,
                "status", "error",
                "error", e.getMessage()
        )));
    }
}