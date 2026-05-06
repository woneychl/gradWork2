@RestController
@RequiredArgsConstructor
public class AssetController {

    private final AssetService assetService;

    @GetMapping("/integrated-assets/{userEmail}")
    public Mono<ResponseEntity<Map<String, Object>>> getAllAssets(@PathVariable String userEmail) {
        return assetService.getIntegratedAssets(userEmail)
                .map(ResponseEntity::ok)
                .defaultIfEmpty(ResponseEntity.notFound().build());
    }
}