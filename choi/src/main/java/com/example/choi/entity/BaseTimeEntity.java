package com.example.choi.entity; // 패키지 경로 확인

import jakarta.persistence.EntityListeners;
import jakarta.persistence.MappedSuperclass;
import lombok.Getter;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Getter
@MappedSuperclass // 5. 모델들이 상속받을 기본 클래스 역할
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseTimeEntity {
    // 모든 테이블에 공통적으로 들어갈 생성일, 수정일 등을 정의합니다.
    @CreatedDate
    private LocalDateTime createdAt;
}