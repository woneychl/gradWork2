package com.example.choi.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.GenericGenerator;
import java.util.UUID;

@Entity
@Table(name = "cards")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Card {
    @Id
    @GeneratedValue(generator = "UUID")
    @GenericGenerator(name = "UUID", strategy = "org.hibernate.id.UUIDGenerator")
    private UUID accountId;

    @Column(nullable = false)
    private String cardNumber;

    private String cardName;

    private String cardType; // 체크/신용 등

    private String cvc;

    private String expiryDate; // 보통 "MM/YY" 형식

    private Long limitAmount; // 한도 금액

    @Column(columnDefinition = "TEXT")
    private String benefits; // 혜택 정보 (내용이 길 수 있으므로 TEXT)

    @Builder.Default
    private Boolean isActive = true;

    // 만약 유저와도 연결되어 있다면 추가 (유저별 조회를 위해 필요)
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    private User user;
}