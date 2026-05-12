package com.example.choi;

import com.example.choi.entity.Card;
import com.example.choi.entity.User;
import com.example.choi.repo.CardRepo;
import lombok.RequiredArgsConstructor;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AssetService {

    private final JwtUtil jwtUtil;
    private final UserService userService;
    private final CardRepo cardRepo;
    private final WebClient webClient = WebClient.builder().build();

    private final Map<String, String> BANK_URLS = Map.of(
            "하나은행", "http://127.0.0.1:8001/user/assets",
            "국민은행", "http://127.0.0.1:8002/user/assets",
            "누리은행", "http://127.0.0.1:8003/user/assets"
    );

    public Mono<Map<String, Object>> getIntegratedAssets(String userEmail, String token) {
        if (token == null || !jwtUtil.validateToken(token, userEmail)) {
            // 인증 실패 시 데이터를 아예 안 찾고 바로 에러를 던집니다.
            return Mono.error(new SecurityException("인증되지 않은 사용자의 접근입니다."));
        }
        // 1. 유저 조회
        User user = userService.getUserByEmail(userEmail);
        // 2. DB에서 이 유저의 카드 목록을 가져옴 (변수명 변경: dbCardList)
        List<Card> myRegisteredCards = cardRepo.findByUser_UserId(user.getUserId());

        // [은행 API] 각 가상 은행 서버 호출 태스크 생성
        List<Mono<Map<String, Object>>> tasks = BANK_URLS.entrySet().stream()
                .map(entry -> fetchBankData(entry.getKey(), entry.getValue(), userEmail))
                .collect(Collectors.toList());

        // 4. 모든 API 호출 결과를 합침
        return Mono.zip(tasks, responses -> {
            long totalBalance = 0;
            List<Map<String, Object>> allAccounts = new ArrayList<>();
            List<Map<String, Object>> allTransactions = new ArrayList<>();
            List<Map<String, Object>> bankCards = new ArrayList<>();

            for (Object obj : responses) {
                Map<String, Object> res = (Map<String, Object>) obj;
                String bankName = (String) res.get("bank");

                // 계좌 정보 처리
                List<Map<String, Object>> accounts = (List<Map<String, Object>>) res.get("accounts");
                if (accounts != null) {
                    for (Map<String, Object> acc : accounts) {
                        totalBalance += ((Number) acc.getOrDefault("balance", 0)).longValue();
                        acc.put("bank_origin", bankName);
                        allAccounts.add(acc);
                    }
                }
                // 은행 서버의 내 카드 정보 처리
                List<Map<String, Object>> cards = (List<Map<String, Object>>) res.get("my_cards");
                if (cards != null) {
                    cards.forEach(c -> c.put("bank_origin", bankName));
                    bankCards.addAll(cards);
                }

                // 최근 거래 내역 정보 처리
                List<Map<String, Object>> transactions = (List<Map<String, Object>>) res.get("transactions");
                if (transactions != null) {
                    transactions.forEach(t -> t.put("bank_origin", bankName));
                    allTransactions.add(Map.of("bank", bankName, "data", transactions));
                }
            }

            Map<String, Object> result = new HashMap<>();
            result.put("user_name", user.getUsername());
            result.put("total_balance", totalBalance);
            result.put("accounts", allAccounts);
            result.put("transactions", allTransactions);

            // 데이터 구분: 중앙 DB에 등록된 카드 vs 은행 API에서 긁어온 실시간 카드
            result.put("my_registered_cards", myRegisteredCards);
            result.put("available_bank_cards", bankCards);

            return result;
        });
    }

    private Mono<Map<String, Object>> fetchBankData(String bankName, String url, String email) {
        return webClient.get()
                .uri(url + "/" + email)
                .retrieve()
                // 파이썬 서버 응답이 이제 List가 아니라 Map(status, accounts, my_cards 등 포함)이므로 수정
                .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                .onErrorReturn(Map.of("bank", bankName, "status", "error", "accounts", Collections.emptyList()));
    }
}