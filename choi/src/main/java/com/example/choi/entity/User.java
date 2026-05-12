package com.example.choi.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.GenericGenerator;
import java.util.UUID;

@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {
    @Id
    @GeneratedValue(generator = "UUID")
    @GenericGenerator(name = "UUID", strategy = "org.hibernate.id.UUIDGenerator")
    @Column(updatable = false, nullable = false)
    private UUID userId; // 모든 서버가 공유할 고유 식별자

    @Column(unique = true, nullable = false)
    private String email;

    @Column(name = "hashed_password",nullable = false)
    private String password; // 로그인용

    private String username;

    @Builder.Default
    private Boolean isActive = true;


}


