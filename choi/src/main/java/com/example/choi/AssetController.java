package com.example.choi; // 프로젝트 구조에 맞는 패키지 선언

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

import java.util.Map;

@RestController
@RequiredArgsConstructor
public class AssetController {

    private final AssetService assetService;

    @GetMapping("/integrated-assets/{userEmail}")
    public Mono<ResponseEntity<Map<String, Object>>> getAllAssets(@PathVariable String userEmail,
        @RequestHeader("Authorization") String bearerToken
    ) {
        String token = bearerToken.substring(7);
        return assetService.getIntegratedAssets(userEmail, token)
                .map(ResponseEntity::ok)
                .defaultIfEmpty(ResponseEntity.notFound().build());
    }
}